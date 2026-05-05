import pytest

from app.config import settings
from app.services import stt_service


# =========================
# Tests STT mock
# =========================

def test_transcrire_audio_mode_mock(monkeypatch):
    monkeypatch.setattr(settings, "stt_provider", "mock")

    resultat = stt_service.transcrire_audio("fake_audio.wav")

    assert resultat == "Quel temps fera-t-il à Paris demain ?"


# =========================
# Tests sécurité config
# =========================

def test_transcrire_audio_whisper_sans_cle_api(monkeypatch):
    monkeypatch.setattr(settings, "stt_provider", "whisper")
    monkeypatch.setattr(settings, "openai_api_key", None)

    with pytest.raises(ValueError) as erreur:
        stt_service.transcrire_audio("fake_audio.wav")

    assert "OPENAI_API_KEY manquante" in str(erreur.value)


# =========================
# Tests Whisper avec OpenAI mocké
# =========================

def test_transcrire_audio_whisper_succes(monkeypatch, tmp_path):
    # Création d'un faux fichier audio temporaire
    audio_file = tmp_path / "audio.wav"
    audio_file.write_bytes(b"fake audio content")

    monkeypatch.setattr(settings, "stt_provider", "whisper")
    monkeypatch.setattr(settings, "openai_api_key", "fake-api-key")

    class FakeTranscription:
        text = "Météo à Lyon demain"

    class FakeTranscriptions:
        def create(self, model, file, language):
            assert model == "whisper-1"
            assert language == "fr"
            assert file is not None
            return FakeTranscription()

    class FakeAudio:
        transcriptions = FakeTranscriptions()

    class FakeOpenAIClient:
        audio = FakeAudio()

    def fake_openai(api_key):
        assert api_key == "fake-api-key"
        return FakeOpenAIClient()

    monkeypatch.setattr(stt_service, "OpenAI", fake_openai)

    resultat = stt_service.transcrire_audio(str(audio_file))

    assert resultat == "Météo à Lyon demain"