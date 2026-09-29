"""
WebSocket endpoint(s) for live battles.

Owner: Backend teammate
This is where players connect, get matched into a battle session,
and send/receive move-selection messages. Should call into
backend.engine for all actual battle logic -- this file should
stay "thin" (routing + validation only).
"""
