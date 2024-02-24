import torch
import torchaudio
from torchaudio.transforms import Resample
from neutone_sdk.audio import AudioSample
import io

class RAVEModelWrapper:
    def __init__(self, model_path):
        self.model = torch.jit.load(model_path).eval()
        self.target_sample_rate = 48000

    def load_audio(self, audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        return waveform, sample_rate

    def resample_audio(self, waveform, orig_sample_rate):
        if orig_sample_rate != self.target_sample_rate:
            resampler = Resample(orig_freq=orig_sample_rate, new_freq=self.target_sample_rate)
            waveform = resampler(waveform)
        return waveform

    def do_forward_pass(self, waveform, params):
        # Clone the input waveform to avoid modifying the original tensor in-place
        waveform = waveform.clone().detach()

        if waveform.dim() == 2:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        waveform = waveform.unsqueeze(0)

        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0).repeat(2, 1)

        z = self.model.encode(waveform)

        noise_amp = params.get("Chaos", 0.5)
        z = torch.randn_like(z) * noise_amp + z

        idx_z = int(params.get("Z edit index", 0.5) * self.model.latent_size)
        idx_z = min(max(idx_z, 0), self.model.latent_size - 1)
        z_scale = params.get("Z scale", 1.0) * 2
        z_offset = params.get("Z offset", 0.0) * 2 - 1

        # Ensure no in-place operation on the tensor that requires gradients
        z = z.clone().detach()
        z[:, idx_z] = z[:, idx_z] * z_scale + z_offset

        out = self.model.decode(z)
        out = out.squeeze(0)

        return out

    def transform_audio(self, input_audio_path, output_audio_path, params):
        waveform, sample_rate = self.load_audio(input_audio_path)
        waveform = self.resample_audio(waveform, sample_rate)
        transformed_waveform = self.do_forward_pass(waveform, params)
        torchaudio.save(output_audio_path, transformed_waveform.cpu(), self.target_sample_rate)

    def render_audio_sample(self, input_audio_sample, params):
        waveform = input_audio_sample.audio
        sample_rate = input_audio_sample.sr

        waveform = self.resample_audio(waveform, sample_rate)
        transformed_waveform = self.do_forward_pass(waveform, params)

        return AudioSample(transformed_waveform, self.target_sample_rate)

def audio_sample_to_mp3_bytes(audio_sample):
    """
    Convert the audio sample to MP3 bytes.
    """
    with io.BytesIO() as buffer:
        # Write the audio data to the buffer as MP3 format
        torchaudio.save(buffer, audio_sample.audio, audio_sample.sr, format='mp3')
        return buffer.getvalue()

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

#     # Transform audio and save
#     rave_wrapper.transform_audio(input_audio_path, output_audio_path, params)
#     print(f"Transformed audio saved to {output_audio_path}")

#     # Render audio sample and save
#     input_audio_sample = AudioSample.from_file(input_audio_path)
#     output_audio_sample = rave_wrapper.render_audio_sample(input_audio_sample, params)
#     with open(output_audio_path, "wb") as f:
#         f.write(audio_sample_to_mp3_bytes(output_audio_sample))
#     print(f"Rendered audio sample saved to {output_audio_path}")

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
