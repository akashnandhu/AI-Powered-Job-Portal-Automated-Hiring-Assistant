# Integrity & Malpractice Detection Framework

This framework specifies the **observable signals, network boundary topologies, and sensory trackers** that continuously evaluate candidate session integrity during virtual job assessments. It operates as a privacy-preserving audit assistant, mapping raw device telemetry into secure, verifiable compliance vectors.

---

## 1. System Topology & Video Telemetry Pipeline

The Integrity Detection System processes browser event boundaries, facial meshes, and audio signatures to verify that the registered candidate is answering the questions without external aid or window navigation:

```mermaid
graph TD
    %% Define Nodes
    Browser[Browser Client UI] -->|1. window.blur / visibilitychange| TabTracker[Tab & Focus Monitor]
    Webcam[Webcam Video Stream] -->|2. Gaze Vector / Yaw Pose| GazeTracker[Visual Integrity Analyzer]
    Audio[Audio Input Stream] -->|3. Pitch & Voice Print| VoiceTracker[Acoustic Diarization Engine]
    
    TabTracker & GazeTracker & VoiceTracker -->|Telemetry Logs JSON| Gateway[API gateway / WebSocket]
    
    subgraph Integrity Scorer Core
        Gateway -->|Stream Logs| Parser[Session Event Parser]
        Parser -->|Tab Navigation Events| TabLogic[Focus Loss Evaluator]
        Parser -->|Gaze & Yaw Outliers| VisualLogic[Visual Malpractice Engine]
        Parser -->|Speaker Overlaps| AudioLogic[Second Speaker Detector]
        
        TabLogic & VisualLogic & AudioLogic -->|Telemetry Flags| FlaggingEngine[Risk Flagging System]
    end
    
    subgraph Unified scoring & Dashboard
        FlaggingEngine -->|Risk Tag: Green/Yellow/Red| RecruiterDashboard[Recruiter Review Dashboard]
        FlaggingEngine -->|Integrity Index: 0-100%| UnifiedScorer[Unified Hiring Scorer]
    end
    
    %% Styling
    classDef client fill:#e1f5fe,stroke:#039be5,stroke-width:2px;
    classDef core fill:#e8f5e9,stroke:#43a047,stroke-width:2px;
    classDef output fill:#fff3e0,stroke:#fb8c00,stroke-width:2px;
    class Browser,Webcam,Audio,TabTracker,GazeTracker,VoiceTracker client;
    class Parser,TabLogic,VisualLogic,AudioLogic,FlaggingEngine core;
    class RecruiterDashboard,UnifiedScorer output;
```

---

## 2. Observable Malpractice Signals

### A. Tab Switching Frequency ($N_{tab}$)
*   **Physics of the Gaze**: Captured via browser tab focus loops (`document.visibilityState`).
*   **Significance**: Measures how often the candidate minimizes the interview screen or moves to other browser tabs to lookup answers.

### B. Loss of Screen Focus ($T_{blur}$)
*   **Physics of the Gaze**: Monitored via HTML5 focus/blur API hooks on the client window scope.
*   **Significance**: Tracks the cumulative duration the candidate spends interacting with outside application layers (e.g. text documents, AI helpers, communications).

### C. Acoustic Speaker Diarization ($V_{ext}$)
*   **Physics of the Gaze**: Processed using audio-frequency pitch analysis and acoustic voice-print validation.
*   **Significance**: Detects when a second distinct voice signature occurs concurrently with the interview audio, indicating an accomplice feeding answers in the background.

### D. Repeated Gaze Deviations ($G_{away}$)
*   **Physics of the Gaze**: Evaluates coordinates $(g_x, g_y)$ alongside head Pose Yaw angles from the `BehavioralScorer`.
*   **Significance**: Detects a candidate consistently looking off-camera (typically towards a physical accomplice or secondary mobile device) while speaking.
