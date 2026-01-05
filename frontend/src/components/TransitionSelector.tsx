import React, { useState, useEffect } from "react";
import axios from "axios";
import "./TransitionSelector.css";

interface Transition {
  name: string;
  description: string;
}

interface Props {
  onTransitionSelect?: (transition: string, duration: number) => void;
}

export function TransitionSelector({ onTransitionSelect }: Props) {
  const [transitions, setTransitions] = useState<Record<string, Transition>>({});
  const [selectedTransition, setSelectedTransition] = useState("dissolve");
  const [duration, setDuration] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTransitions();
  }, []);

  const fetchTransitions = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/transitions/available");
      setTransitions(response.data.transitions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTransitionChange = (transitionName: string) => {
    setSelectedTransition(transitionName);
    onTransitionSelect?.(transitionName, duration);
  };

  const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDuration = parseFloat(e.target.value);
    setDuration(newDuration);
    onTransitionSelect?.(selectedTransition, newDuration);
  };

  if (loading) return <div className="transition-selector loading">Loading...</div>;
  if (error) return <div className="transition-selector error">Error: {error}</div>;

  const currentTransition = transitions[selectedTransition];

  return (
    <div className="transition-selector">
      <div className="selector-header">
        <h3>Video Transitions</h3>
        <p className="total-count">{Object.keys(transitions).length}+ effects</p>
      </div>

      <div className="transition-grid">
        {Object.entries(transitions).map(([name, trans]) => (
          <button
            type="button"
            key={name}
            className={`transition-button ${selectedTransition === name ? "selected" : ""}`}
            onClick={() => handleTransitionChange(name)}
            title={trans.description}
          >
            {name}
            {selectedTransition === name && <span className="checkmark">✓</span>}
          </button>
        ))}
      </div>

      {currentTransition && (
        <div className="selection-info">
          <h4>{currentTransition.name}</h4>
          <p>{currentTransition.description}</p>
        </div>
      )}

      <div className="duration-control">
        <label>
          <span className="label-text">Duration: {duration.toFixed(1)}s</span>
          <input
            type="range"
            min="0.5"
            max="5"
            step="0.1"
            value={duration}
            onChange={handleDurationChange}
            className="duration-slider"
          />
        </label>
      </div>

      <button
        type="button"
        className="btn btn-primary"
        onClick={() => onTransitionSelect?.(selectedTransition, duration)}
      >
        Apply Transition
      </button>
    </div>
  );
}
