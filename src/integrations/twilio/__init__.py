"""
Twilio Integration for Bambu Agent System
Enables phone calls and SMS for AI avatar
"""

import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say, Gather
import requests


class TwilioIntegration:
    """Twilio phone and SMS integration"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_SECRET")
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid and self.auth_token else None
        
    def make_call(
        self,
        to_number: str,
        from_number: str,
        twiml_url: Optional[str] = None,
        twiml: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an outbound call"""
        
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            call_params = {
                "to": to_number,
                "from_": from_number
            }
            
            if twiml_url:
                call_params["url"] = twiml_url
            elif twiml:
                call_params["twiml"] = twiml
            else:
                # Default greeting
                response = VoiceResponse()
                response.say("Hello! This is Bambu, your AI assistant. How can I help you today?")
                call_params["twiml"] = str(response)
            
            call = self.client.calls.create(**call_params)
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_sms(
        self,
        to_number: str,
        from_number: str,
        message: str
    ) -> Dict[str, Any]:
        """Send an SMS message"""
        
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                to=to_number,
                from_=from_number
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": message_obj.to,
                "from": message_obj.from_
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """Get status of a call"""
        
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "success": True,
                "status": call.status,
                "duration": call.duration,
                "price": call.price,
                "direction": call.direction
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_call_logs(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent call logs"""
        
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            calls = self.client.calls.list(limit=limit)
            return {
                "success": True,
                "calls": [
                    {
                        "sid": call.sid,
                        "to": call.to,
                        "from": call.from_,
                        "status": call.status,
                        "duration": call.duration,
                        "date_created": str(call.date_created)
                    }
                    for call in calls
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_twiml_for_ai_conversation(
        self,
        greeting: str = "Hello, this is Bambu. How can I help you?",
        action_url: str = "/voice/handle-response"
    ) -> str:
        """Create TwiML for AI-powered conversation"""
        
        response = VoiceResponse()
        
        # Say greeting
        response.say(greeting, voice="alice")
        
        # Gather user input
        gather = Gather(
            input="speech dtmf",
            action=action_url,
            method="POST",
            speech_timeout="auto"
        )
        gather.say("Please speak after the tone.")
        response.append(gather)
        
        # If no input, say goodbye
        response.say("I didn't hear anything. Goodbye!")
        
        return str(response)
    
    def create_twiml_response(self, text: str) -> str:
        """Create simple TwiML response"""
        response = VoiceResponse()
        response.say(text, voice="alice")
        return str(response)
    
    def get_available_numbers(self, country_code: str = "US") -> Dict[str, Any]:
        """Get available phone numbers"""
        
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            numbers = self.client.available_phone_numbers(country_code).local.list(limit=10)
            return {
                "success": True,
                "numbers": [
                    {
                        "phone_number": num.phone_number,
                        "friendly_name": num.friendly_name,
                        "locality": num.locality,
                        "region": num.region
                    }
                    for num in numbers
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def call_number(to_number: str, from_number: str, message: str = None) -> Dict[str, Any]:
    """Quick function to make a call"""
    twilio = TwilioIntegration()
    
    if message:
        twiml = twilio.create_twiml_response(message)
        return twilio.make_call(to_number, from_number, twiml=twiml)
    else:
        return twilio.make_call(to_number, from_number)


def send_text(to_number: str, from_number: str, message: str) -> Dict[str, Any]:
    """Quick function to send SMS"""
    twilio = TwilioIntegration()
    return twilio.send_sms(to_number, from_number, message)


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python twilio.py [call|sms|status|logs]")
        sys.exit(1)
    
    command = sys.argv[1]
    twilio = TwilioIntegration()
    
    if command == "call":
        if len(sys.argv) < 4:
            print("Usage: python twilio.py call <to_number> <from_number> [message]")
            sys.exit(1)
        to_num = sys.argv[2]
        from_num = sys.argv[3]
        message = sys.argv[4] if len(sys.argv) > 4 else None
        result = call_number(to_num, from_num, message)
        print(json.dumps(result, indent=2))
    elif command == "sms":
        if len(sys.argv) < 5:
            print("Usage: python twilio.py sms <to_number> <from_number> <message>")
            sys.exit(1)
        result = send_text(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))
    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: python twilio.py status <call_sid>")
            sys.exit(1)
        result = twilio.get_call_status(sys.argv[2])
        print(json.dumps(result, indent=2))
    elif command == "logs":
        result = twilio.get_call_logs()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")
