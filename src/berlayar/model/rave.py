# berlayar/src/berlayar/model/rave.py

import torch
import torchaudio
from torchaudio.transforms import Resample
from pathlib import Path

class RAVEModelWrapper:
    def __init__(self, model_path):
        self.model = torch.jit.load(model_path).eval()  # Load the model in evaluation mode
        self.target_sample_rate = 48000  # Define target sample rate

    def load_audio(self, audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        return waveform, sample_rate

    def resample_audio(self, waveform, orig_sample_rate):
        if orig_sample_rate != self.target_sample_rate:
            resampler = Resample(orig_freq=orig_sample_rate, new_freq=self.target_sample_rate)
            waveform = resampler(waveform)
        return waveform

    def do_forward_pass(self, waveform, params):
        # Ensure mono audio and add batch dimension
        if waveform.dim() == 2:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        waveform = waveform.unsqueeze(0)  # Adding batch dimension

        # Convert mono to stereo by duplicating the channel
        if waveform.dim() == 1:  # Mono to Stereo for a model trained on stereo
            waveform = waveform.unsqueeze(0).repeat(2, 1)

        # Encoding step (assuming your model has an encode method)
        z = self.model.encode(waveform)  # Adjust according to your model's method

        # Manipulate latent variable as described
        noise_amp = params.get("Chaos", 0.5)
        z = torch.randn_like(z) * noise_amp + z

        idx_z = int(params.get("Z edit index", 0.5) * self.model.latent_size)
        idx_z = min(max(idx_z, 0), self.model.latent_size - 1)  # Ensure idx_z is within valid range
        z_scale = params.get("Z scale", 1.0) * 2
        z_offset = params.get("Z offset", 0.0) * 2 - 1
        z[:, idx_z] = z[:, idx_z] * z_scale + z_offset

        out = self.model.decode(z)
        out = out.squeeze(0)  # Remove batch dimension for saving

        return out

    def transform_audio(self, input_audio_path, output_audio_path, params):
        waveform, sample_rate = self.load_audio(input_audio_path)
        waveform = self.resample_audio(waveform, sample_rate)
        transformed_waveform = self.do_forward_pass(waveform, params)
        torchaudio.save(output_audio_path, transformed_waveform.cpu(), self.target_sample_rate)

# if __name__ == "__main__":
#     model_path = "/home/erniesg/code/erniesg/raw_data/models/darbouka_onnx.ts"
#     input_audio_path = "/home/erniesg/code/erniesg/raw_data/kingfisher.mp3"
#     output_audio_path = "/home/erniesg/code/erniesg/raw_data/kingfisher_out.mp3"
#     params = {
#         "Chaos": 0.5,  # Example parameter for latent noise magnitude
#         "Z edit index": 0.2,  # Example parameter for latent dimension index to edit
#         "Z scale": 1.0,  # Example parameter for scale of latent variable
#         "Z offset": 0.0,  # Example parameter for offset of latent variable
#     }

#     rave_wrapper = RAVEModelWrapper(model_path)
#     rave_wrapper.transform_audio(input_audio_path, output_audio_path, params)
#     print(f"Transformed audio saved to {output_audio_path}")
