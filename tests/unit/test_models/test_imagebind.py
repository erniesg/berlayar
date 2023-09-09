import unittest
from unittest.mock import patch, MagicMock
import torch
from src.models.imagebind_model_wrapper import ImageBindModelWrapper, ModalityType

class TestImageBindModelWrapper(unittest.TestCase):

    def setUp(self):
        self.wrapper = ImageBindModelWrapper()

    @patch("src.models.imagebind_model_wrapper.data.load_and_transform_vision_data", return_value=torch.randn(1, 3, 224, 224))
    @patch.object(ImageBindModelWrapper, "model", create=True)
    def test_get_image_embeddings(self, mock_model, mock_data_transform):
        mock_model.return_value = {ModalityType.VISION: torch.tensor([[0.5, 0.5]])}
        dummy_image_path = ["path/to/dummy/image.jpg"]
        embeddings = self.wrapper.get_image_embeddings(dummy_image_path)
        self.assertEqual(embeddings.shape, (1, 2))

    @patch("src.models.imagebind_model_wrapper.data.load_and_transform_text", return_value=torch.randn(1, 10))
    @patch.object(ImageBindModelWrapper, "model", create=True)
    def test_get_text_embeddings(self, mock_model, mock_data_transform):
        mock_model.return_value = {ModalityType.TEXT: torch.tensor([[0.7, 0.3]])}
        dummy_text = ["This is a test"]
        embeddings = self.wrapper.get_text_embeddings(dummy_text)
        self.assertEqual(embeddings.shape, (1, 2))

    @patch("src.models.imagebind_model_wrapper.data.load_and_transform_audio_data", return_value=torch.randn(1, 40, 12))
    @patch.object(ImageBindModelWrapper, "model", create=True)
    def test_get_audio_embeddings(self, mock_model, mock_data_transform):
        mock_model.return_value = {ModalityType.AUDIO: torch.tensor([[0.6, 0.4]])}
        dummy_audio_path = ["path/to/dummy/audio.wav"]
        embeddings = self.wrapper.get_audio_embeddings(dummy_audio_path)
        self.assertEqual(embeddings.shape, (1, 2))

if __name__ == "__main__":
    unittest.main()
