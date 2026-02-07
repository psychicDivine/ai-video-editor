/**
 * EditPlanContext - State management for the EditPlan editing workflow
 */
import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import {
  EditPlan,
  EditClip,
  Effect,
  EditPlanState,
  EditPlanResponse,
  EffectCatalog,
  TransitionCatalog,
  StyleCatalog,
  StyleType,
  TransitionType,
} from '../types/EditPlan';

// ============== ACTIONS ==============

type EditPlanAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_GENERATING'; payload: boolean }
  | { type: 'SET_RENDERING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_PLAN'; payload: EditPlan | null }
  | { type: 'UPDATE_CLIP'; payload: EditClip }
  | { type: 'REORDER_CLIPS'; payload: EditClip[] }
  | { type: 'ADD_CLIP'; payload: EditClip }
  | { type: 'REMOVE_CLIP'; payload: string }
  | { type: 'ADD_EFFECT'; payload: { clipId: string; effect: Effect } }
  | { type: 'REMOVE_EFFECT'; payload: { clipId: string; effectIndex: number } }
  | { type: 'SET_TRANSITION'; payload: { clipId: string; transition: TransitionType; duration: number } }
  | { type: 'SET_STYLE'; payload: StyleType }
  | { type: 'SET_TIMELINE_TIME'; payload: number }
  | { type: 'SET_TIMELINE_ZOOM'; payload: number }
  | { type: 'SELECT_CLIP'; payload: string | null }
  | { type: 'SET_DRAGGING'; payload: boolean }
  | { type: 'SET_CATALOGS'; payload: { effects: EffectCatalog; transitions: TransitionCatalog; styles: StyleCatalog } };

// ============== INITIAL STATE ==============

const initialState: EditPlanState = {
  plan: null,
  isLoading: false,
  isGenerating: false,
  isRendering: false,
  error: null,
  timeline: {
    currentTime: 0,
    zoom: 1,
    selectedClipId: null,
    isDragging: false,
  },
  catalogs: {
    effects: {},
    transitions: {},
    styles: {},
  },
};

// ============== REDUCER ==============

function editPlanReducer(state: EditPlanState, action: EditPlanAction): EditPlanState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_GENERATING':
      return { ...state, isGenerating: action.payload };
    
    case 'SET_RENDERING':
      return { ...state, isRendering: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'SET_PLAN':
      return { ...state, plan: action.payload, error: null };
    
    case 'UPDATE_CLIP':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: state.plan.clips.map(c => 
            c.id === action.payload.id ? action.payload : c
          ),
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'REORDER_CLIPS':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: action.payload,
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'ADD_CLIP':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: [...state.plan.clips, action.payload],
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'REMOVE_CLIP':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: state.plan.clips.filter(c => c.id !== action.payload),
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'ADD_EFFECT':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: state.plan.clips.map(c => 
            c.id === action.payload.clipId 
              ? { ...c, effects: [...c.effects, action.payload.effect] }
              : c
          ),
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'REMOVE_EFFECT':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: state.plan.clips.map(c => 
            c.id === action.payload.clipId 
              ? { 
                  ...c, 
                  effects: c.effects.filter((_, i) => i !== action.payload.effectIndex) 
                }
              : c
          ),
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'SET_TRANSITION':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          clips: state.plan.clips.map(c => 
            c.id === action.payload.clipId 
              ? { 
                  ...c, 
                  transition_in: action.payload.transition,
                  transition_in_duration: action.payload.duration,
                }
              : c
          ),
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'SET_STYLE':
      if (!state.plan) return state;
      return {
        ...state,
        plan: {
          ...state.plan,
          style: action.payload,
          updated_at: new Date().toISOString(),
        },
      };
    
    case 'SET_TIMELINE_TIME':
      return {
        ...state,
        timeline: { ...state.timeline, currentTime: action.payload },
      };
    
    case 'SET_TIMELINE_ZOOM':
      return {
        ...state,
        timeline: { ...state.timeline, zoom: action.payload },
      };
    
    case 'SELECT_CLIP':
      return {
        ...state,
        timeline: { ...state.timeline, selectedClipId: action.payload },
      };
    
    case 'SET_DRAGGING':
      return {
        ...state,
        timeline: { ...state.timeline, isDragging: action.payload },
      };
    
    case 'SET_CATALOGS':
      return {
        ...state,
        catalogs: action.payload,
      };
    
    default:
      return state;
  }
}

// ============== CONTEXT ==============

interface EditPlanContextValue {
  state: EditPlanState;
  dispatch: React.Dispatch<EditPlanAction>;
  
  // Actions
  generatePlan: (jobId: string, style: StyleType, videoPaths: string[], audioPath: string, duration: number) => Promise<void>;
  updatePlan: () => Promise<void>;
  renderPlan: (quality?: 'draft' | 'medium' | 'high') => Promise<void>;
  loadCatalogs: () => Promise<void>;
  
  // Clip operations
  updateClip: (clip: EditClip) => void;
  reorderClips: (clips: EditClip[]) => void;
  addClip: (clip: EditClip) => void;
  removeClip: (clipId: string) => void;
  
  // Effect operations
  addEffect: (clipId: string, effect: Effect) => void;
  removeEffect: (clipId: string, effectIndex: number) => void;
  
  // Transition operations
  setTransition: (clipId: string, transition: TransitionType, duration: number) => void;
  
  // Timeline operations
  setCurrentTime: (time: number) => void;
  setZoom: (zoom: number) => void;
  selectClip: (clipId: string | null) => void;
}

const EditPlanContext = createContext<EditPlanContextValue | null>(null);

// ============== PROVIDER ==============

interface EditPlanProviderProps {
  children: ReactNode;
}

export function EditPlanProvider({ children }: EditPlanProviderProps) {
  const [state, dispatch] = useReducer(editPlanReducer, initialState);

  const generatePlan = useCallback(async (
    jobId: string,
    style: StyleType,
    videoPaths: string[],
    audioPath: string,
    duration: number
  ) => {
    dispatch({ type: 'SET_GENERATING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const response = await fetch('/api/plan/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          style,
          target_duration: duration,
          video_paths: videoPaths,
          audio_path: audioPath,
        }),
      });
      
      const data: EditPlanResponse = await response.json();
      
      if (data.success && data.plan) {
        dispatch({ type: 'SET_PLAN', payload: data.plan });
      } else {
        dispatch({ type: 'SET_ERROR', payload: data.message || 'Failed to generate plan' });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: String(error) });
    } finally {
      dispatch({ type: 'SET_GENERATING', payload: false });
    }
  }, []);

  const updatePlan = useCallback(async () => {
    if (!state.plan) return;
    
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch(`/api/plan/${state.plan.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clips: state.plan.clips,
          audio: state.plan.audio,
          style: state.plan.style,
        }),
      });
      
      const data: EditPlanResponse = await response.json();
      
      if (!data.success) {
        dispatch({ type: 'SET_ERROR', payload: data.message || 'Failed to update plan' });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: String(error) });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.plan]);

  const renderPlan = useCallback(async (quality: 'draft' | 'medium' | 'high' = 'high') => {
    if (!state.plan) return;
    
    dispatch({ type: 'SET_RENDERING', payload: true });
    
    try {
      const response = await fetch(`/api/plan/${state.plan.id}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: state.plan.id,
          quality,
          output_format: 'mp4',
        }),
      });
      
      const data: EditPlanResponse = await response.json();
      
      if (!data.success) {
        dispatch({ type: 'SET_ERROR', payload: data.message || 'Failed to start render' });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: String(error) });
    } finally {
      dispatch({ type: 'SET_RENDERING', payload: false });
    }
  }, [state.plan]);

  const loadCatalogs = useCallback(async () => {
    try {
      const [effectsRes, transitionsRes, stylesRes] = await Promise.all([
        fetch('/api/plan/catalog/effects'),
        fetch('/api/plan/catalog/transitions'),
        fetch('/api/plan/catalog/styles'),
      ]);
      
      const [effectsData, transitionsData, stylesData] = await Promise.all([
        effectsRes.json(),
        transitionsRes.json(),
        stylesRes.json(),
      ]);
      
      dispatch({
        type: 'SET_CATALOGS',
        payload: {
          effects: effectsData.effects || {},
          transitions: transitionsData.transitions || {},
          styles: stylesData.styles || {},
        },
      });
    } catch (error) {
      console.error('Failed to load catalogs:', error);
    }
  }, []);

  // Clip operations
  const updateClip = useCallback((clip: EditClip) => {
    dispatch({ type: 'UPDATE_CLIP', payload: clip });
  }, []);

  const reorderClips = useCallback((clips: EditClip[]) => {
    dispatch({ type: 'REORDER_CLIPS', payload: clips });
  }, []);

  const addClip = useCallback((clip: EditClip) => {
    dispatch({ type: 'ADD_CLIP', payload: clip });
  }, []);

  const removeClip = useCallback((clipId: string) => {
    dispatch({ type: 'REMOVE_CLIP', payload: clipId });
  }, []);

  // Effect operations
  const addEffect = useCallback((clipId: string, effect: Effect) => {
    dispatch({ type: 'ADD_EFFECT', payload: { clipId, effect } });
  }, []);

  const removeEffect = useCallback((clipId: string, effectIndex: number) => {
    dispatch({ type: 'REMOVE_EFFECT', payload: { clipId, effectIndex } });
  }, []);

  // Transition operations
  const setTransition = useCallback((clipId: string, transition: TransitionType, duration: number) => {
    dispatch({ type: 'SET_TRANSITION', payload: { clipId, transition, duration } });
  }, []);

  // Timeline operations
  const setCurrentTime = useCallback((time: number) => {
    dispatch({ type: 'SET_TIMELINE_TIME', payload: time });
  }, []);

  const setZoom = useCallback((zoom: number) => {
    dispatch({ type: 'SET_TIMELINE_ZOOM', payload: zoom });
  }, []);

  const selectClip = useCallback((clipId: string | null) => {
    dispatch({ type: 'SELECT_CLIP', payload: clipId });
  }, []);

  const value: EditPlanContextValue = {
    state,
    dispatch,
    generatePlan,
    updatePlan,
    renderPlan,
    loadCatalogs,
    updateClip,
    reorderClips,
    addClip,
    removeClip,
    addEffect,
    removeEffect,
    setTransition,
    setCurrentTime,
    setZoom,
    selectClip,
  };

  return (
    <EditPlanContext.Provider value={value}>
      {children}
    </EditPlanContext.Provider>
  );
}

// ============== HOOK ==============

export function useEditPlan() {
  const context = useContext(EditPlanContext);
  if (!context) {
    throw new Error('useEditPlan must be used within an EditPlanProvider');
  }
  return context;
}

export default EditPlanContext;
