import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Frei0rSelector.css";

interface Preset {
  filter: string;
  params?: string;
}

interface Props {
  onApply?: (outputFile: string) => void;
}

export function Frei0rSelector({ onApply }: Props) {
  const [presets, setPresets] = useState<Record<string, Preset>>({});
  const [selected, setSelected] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPresets();
  }, []);

  const fetchPresets = async () => {
    try {
      setLoading(true);
      const res = await axios.get("/api/frei0r/available");
      setPresets(res.data.presets || {});
      const keys = Object.keys(res.data.presets || {});
      setSelected(keys[0] || "");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files && e.target.files[0];
    setFile(f || null);
  };

  const apply = async () => {
    if (!file) return setError("Select a file first");
    if (!selected) return setError("Select a preset");

    setLoading(true);
    setError(null);
    setResult(null);

    const form = new FormData();
    form.append("preset", selected);
    form.append("file", file);

    try {
      const res = await axios.post("/api/frei0r/apply", form, { headers: { "Content-Type": "multipart/form-data" } });
      setResult(res.data.output_file);
      onApply?.(res.data.output_file);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="frei0r-selector">Loading...</div>;
  if (error) return <div className="frei0r-selector error">Error: {error}</div>;

  return (
    <div className="frei0r-selector">
      <h3>Frei0r Filters</h3>
      <div className="preset-list">
        {Object.entries(presets).map(([k, p]) => (
          <button
            key={k}
            className={`preset-button ${selected === k ? "selected" : ""}`}
            onClick={() => setSelected(k)}
            title={`${p.filter} ${p.params || ""}`}
          >
            {k}
          </button>
        ))}
      </div>

      <div className="file-input">
        <input type="file" accept="video/*" onChange={handleFile} />
      </div>

      <button className="btn btn-primary" onClick={apply} disabled={!file || !selected}>
        Apply Preset
      </button>

      {result && <div className="result">Output: {result}</div>}
    </div>
  );
}
