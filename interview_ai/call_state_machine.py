import logging
from enum import Enum, auto
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CallState(Enum):
    INIT = auto()
    ASK_QUESTION = auto()
    WAITING_FOR_RESPONSE = auto()
    ANALYZING_RESPONSE = auto()
    FOLLOW_UP = auto()
    ERROR_RECOVERY = auto()
    WRAP_UP = auto()
    TERMINATED = auto()

class ErrorType(Enum):
    SILENCE = "silence"
    CONFUSION = "confusion"
    REPEATED_ANSWER = "repeated_answer"
    POOR_AUDIO = "poor_audio"
    LANGUAGE_MIXING = "language_mixing"
    MISSING_ANSWER = "missing_answer"

class ConversationStateMachine:
    """
    Finite State Machine to manage the flow of an AI-driven interview or screening call.
    Handles primary transitions, error recovery (silence, confusion, repeated answers),
    and follow-up probing.
    """
    def __init__(self, questions: List[str]):
        self.state = CallState.INIT
        self.questions = questions
        self.current_question_index = 0
        self.consecutive_errors = 0
        self.max_retries = 2
        self.current_error_type: Optional[ErrorType] = None
        self.context_history: List[Dict[str, Any]] = []

    def transition(self, next_state: CallState):
        """Transitions the machine to a new state."""
        logger.info(f"Transitioning from {self.state.name} to {next_state.name}")
        self.state = next_state

    def process_event(self, event_type: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for processing external events in the state machine.
        Returns the next action and prompt the AI agent should take.
        """
        payload = payload or {}
        response = {"message": "", "action": ""}

        if self.state == CallState.INIT:
            response = self._handle_init()
        elif self.state == CallState.ASK_QUESTION:
            response = self._handle_ask_question()
        elif self.state == CallState.WAITING_FOR_RESPONSE:
            response = self._handle_waiting_for_response(event_type, payload)
        elif self.state == CallState.ANALYZING_RESPONSE:
            response = self._handle_analyzing_response(payload)
        elif self.state == CallState.FOLLOW_UP:
            response = self._handle_follow_up(payload)
        elif self.state == CallState.ERROR_RECOVERY:
            response = self._handle_error_recovery()
        elif self.state == CallState.WRAP_UP:
            response = self._handle_wrap_up()
        elif self.state == CallState.TERMINATED:
            response = {"message": "Call has ended.", "action": "DISCONNECT"}

        return response

    def _handle_init(self) -> Dict[str, Any]:
        self.transition(CallState.ASK_QUESTION)
        return {
            "message": "Hello! Welcome to the interview. Are you ready to begin?",
            "action": "SPEAK_AND_WAIT"
        }

    def _handle_ask_question(self) -> Dict[str, Any]:
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.transition(CallState.WAITING_FOR_RESPONSE)
            return {
                "message": question,
                "action": "SPEAK_AND_WAIT"
            }
        else:
            self.transition(CallState.WRAP_UP)
            return self._handle_wrap_up()

    def _handle_waiting_for_response(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if event_type == "silence_timeout":
            self.current_error_type = ErrorType.SILENCE
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif event_type == "response_received":
            self.transition(CallState.ANALYZING_RESPONSE)
            return self._handle_analyzing_response(payload)
        return {"message": "Waiting...", "action": "WAIT"}

    def _handle_analyzing_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates payload from Understanding/Scoring engine to determine next steps.
        """
        confusion_detected = payload.get("confusion", False)
        repeated_detected = payload.get("repeated", False)
        poor_audio = payload.get("poor_audio", False)
        language_mixed = payload.get("language_mixed", False)
        missing_answer = payload.get("missing_answer", False)
        needs_follow_up = payload.get("needs_follow_up", False)
        
        if poor_audio:
            self.current_error_type = ErrorType.POOR_AUDIO
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif language_mixed:
            self.current_error_type = ErrorType.LANGUAGE_MIXING
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif missing_answer:
            self.current_error_type = ErrorType.MISSING_ANSWER
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif confusion_detected:
            self.current_error_type = ErrorType.CONFUSION
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif repeated_detected:
            self.current_error_type = ErrorType.REPEATED_ANSWER
            self.transition(CallState.ERROR_RECOVERY)
            return self._handle_error_recovery()
        elif needs_follow_up:
            self.transition(CallState.FOLLOW_UP)
            return self._handle_follow_up(payload)
        
        # Answer accepted, move to next question
        self.consecutive_errors = 0
        self.current_question_index += 1
        self.transition(CallState.ASK_QUESTION)
        return {"message": "Great, let's move on to the next question.", "action": "CONTINUE"}

    def _handle_follow_up(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs a dynamic follow-up probe based on vague/incomplete answers.
        """
        follow_up_question = payload.get("follow_up_question", "Could you provide more specific metrics on that?")
        self.transition(CallState.WAITING_FOR_RESPONSE)
        return {
            "message": follow_up_question,
            "action": "SPEAK_AND_WAIT"
        }

    def _handle_error_recovery(self) -> Dict[str, Any]:
        """
        Manages error states up to a max_retry limit.
        """
        self.consecutive_errors += 1
        
        if self.consecutive_errors > self.max_retries:
            self.transition(CallState.WRAP_UP)
            return self._handle_polite_failure()
            
        if self.current_error_type == ErrorType.SILENCE or self.current_error_type == ErrorType.MISSING_ANSWER:
            msg = "I didn't quite catch that. Are you still there?" if self.consecutive_errors == 1 else "Just checking if you are still connected. To repeat the question..."
        elif self.current_error_type == ErrorType.POOR_AUDIO:
            msg = "I'm having a little trouble hearing you clearly due to some background noise. Could you repeat that?" if self.consecutive_errors == 1 else "The audio is still a bit fuzzy. Let's try one more time."
        elif self.current_error_type == ErrorType.LANGUAGE_MIXING:
            msg = "I'm sorry, I primarily understand English. Could you please answer in English?" if self.consecutive_errors == 1 else "Could you try phrasing that in English again?"
        elif self.current_error_type == ErrorType.CONFUSION:
            msg = "Let me rephrase that using simpler terms. " + self.questions[self.current_question_index] if self.consecutive_errors == 1 else "Let's try a simpler fallback question on this topic."
        elif self.current_error_type == ErrorType.REPEATED_ANSWER:
            msg = "It sounds like we touched on that. Could you elaborate specifically on another aspect?" if self.consecutive_errors == 1 else "Let's just move on to the next topic."
            if self.consecutive_errors > 1:
                # Force transition past repeated answers
                self.consecutive_errors = 0
                self.current_question_index += 1
                self.transition(CallState.ASK_QUESTION)
                return {"message": msg, "action": "CONTINUE"}
        else:
            msg = "I'm having trouble understanding. Can you repeat that?"

        self.transition(CallState.WAITING_FOR_RESPONSE)
        return {
            "message": msg,
            "action": "SPEAK_AND_WAIT"
        }

    def _handle_polite_failure(self) -> Dict[str, Any]:
        """
        Polite exit strategy when recovery fails.
        """
        self.transition(CallState.TERMINATED)
        return {
            "message": "It seems we might be experiencing some technical difficulties or having trouble connecting clearly. Let's pause here. Our recruitment team will reach out to you via email to continue this process. Thank you for your time today!",
            "action": "DISCONNECT"
        }

    def _handle_wrap_up(self) -> Dict[str, Any]:
        """
        Standard graceful call termination.
        """
        self.transition(CallState.TERMINATED)
        return {
            "message": "Thank you for taking the time to speak with me today. Have a great day!",
            "action": "DISCONNECT"
        }
