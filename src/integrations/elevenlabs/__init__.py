"""
Eleven Labs Voice Integration for Bambu Agent System
Enables voice synthesis for AI avatar
"""

import os
import requests
from typing import Optional, Dict, Any
import base64


class ElevenLabsIntegration:
    """Eleven Labs voice synthesis integration"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self):
        self.api_key = os.getenv("ELEVEN_LABS_API")
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
    def get_voices(self) -> Dict[str, Any]:
        """Get all available voices"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/voices",
                headers=self.headers
            )
            return {
                "success": response.status_code == 200,
                "voices": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_default_voice(self) -> Optional[str]:
        """Get default voice ID for Bambu"""
        # Professional male voice for Bambu
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional voice
    
    def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Dict[str, Any]:
        """Convert text to speech"""
        
        voice = voice_id or self.get_default_voice()
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/text-to-speech/{voice}",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                # Return audio data as base64
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "content_type": response.headers.get("content-type", "audio/mpeg")
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def text_to_speech_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1"
    ):
        """Stream text to speech (generator)"""
        
        voice = voice_id or self.get_default_voice()
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/text-to-speech/{voice}/stream",
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
                    
        except Exception as e:
            yield None
    
    def create_voice(
        self,
        name: str,
        files: list,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a custom voice"""
        
        try:
            # Prepare files for upload
            files_data = []
            for file_path in files:
                with open(file_path, 'rb') as f:
                    files_data.append(('files', f))
            
            data = {
                'name': name,
                'description': description
            }
            
            response = requests.post(
                f"{self.BASE_URL}/voices/add",
                headers={"xi-api-key": self.api_key},
                files=files_data,
                data=data
            )
            
            return {
                "success": response.status_code == 200,
                "voice_id": response.json().get("voice_id") if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user subscription info"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/user",
                headers=self.headers
            )
            return {
                "success": response.status_code == 200,
                "user": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_character_count(self) -> Dict[str, Any]:
        """Get character usage count"""
        user_info = self.get_user_info()
        if user_info["success"] and user_info["user"]:
            subscription = user_info["user"].get("subscription", {})
            return {
                "success": True,
                "character_count": subscription.get("character_count", 0),
                "character_limit": subscription.get("character_limit", 0)
            }
        return {"success": False}


def speak(text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
    """Quick function to convert text to speech"""
    eleven = ElevenLabsIntegration()
    return eleven.text_to_speech(text, voice_id)


def get_available_voices() -> Dict[str, Any]:
    """Get all available voices"""
    eleven = ElevenLabsIntegration()
    return eleven.get_voices()


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python elevenlabs.py [speak|voices|info]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "speak":
        if len(sys.argv) < 3:
            print("Usage: python elevenlabs.py speak 'text'")
            sys.exit(1)
        text = sys.argv[2]
        result = speak(text)
        print(json.dumps({"success": result["success"]}, indent=2))
    elif command == "voices":
        result = get_available_voices()
        print(json.dumps(result, indent=2))
    elif command == "info":
        eleven = ElevenLabsIntegration()
        result = eleven.get_user_info()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")
