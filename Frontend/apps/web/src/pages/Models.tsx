import { useEffect } from "react";
import { useAppStore } from "../state";
import { modelsApi } from "../api";

export default function Models() {
  const { models, setModels, setError } = useAppStore();

  useEffect(() => {
    modelsApi
      .list()
      .then(setModels)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load models"));
  }, [setModels, setError]);

  const handleLoad = async (id: string) => {
    try {
      await modelsApi.load(id);
      const updated = await modelsApi.list();
      setModels(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load model");
    }
  };

  const handleUnload = async (id: string) => {
    try {
      await modelsApi.unload(id);
      const updated = await modelsApi.list();
      setModels(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to unload model");
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1>Models</h1>
      </header>
      <div className="models-list">
        {models.length === 0 ? (
          <p className="empty">No models available.</p>
        ) : (
          models.map((model) => (
            <div key={model.id} className="model-card">
              <div className="model-info">
                <h3>{model.name}</h3>
                <span className={`model-status ${model.status}`}>{model.status}</span>
                {model.size && <span className="model-size">{model.size}</span>}
                {model.quantized && <span className="model-quant">{model.quantized}</span>}
              </div>
              <div className="model-actions">
                {model.status === "unloaded" && (
                  <button onClick={() => handleLoad(model.id)}>Load</button>
                )}
                {model.status === "loaded" && (
                  <button onClick={() => handleUnload(model.id)}>Unload</button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}