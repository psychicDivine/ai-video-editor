/**
 * EditPlan TypeScript Types
 * Matches backend schema in backend/app/schemas/edit_plan.py
 */

// ============== ENUMS ==============

export type EffectType =
  | 'slowmo'
  | 'speedup'
  | 'speedramp'
  | 'freeze'
  | 'zoomPunch'
  | 'kenburns'
  | 'flashWhite'
  | 'shake'
  | 'vignette'
  | 'colorPulse';

export type TransitionType =
  | 'fade'
  | 'dissolve'
  | 'fadeblack'
  | 'fadewhite'
  | 'wipeleft'
  | 'wiperight'
  | 'wipeup'
  | 'wipedown'
  | 'slideleft'
  | 'slideright'
  | 'slideup'
  | 'slidedown'
  | 'circlecrop'
  | 'circleopen'
  | 'circleclose'
  | 'pixelize'
  | 'radial';

export type StyleType =
  | 'cinematic_drama'
  | 'energetic_dance'
  | 'luxe_travel'
  | 'modern_minimal'
  | 'viral_tiktok';

export type RenderQuality = 'draft' | 'medium' | 'high';

// ============== EFFECT ==============

export interface Effect {
  type: EffectType;
  params: Record<string, number | string | boolean>;
}

export interface EffectMeta {
  name: string;
  description: string;
  params: Record<string, {
    type: string;
    min?: number;
    max?: number;
    default: number | string;
    options?: string[];
  }>;
  energy: 'low' | 'medium' | 'high';
  use_case: string;
}

// ============== TRANSITION ==============

export interface TransitionMeta {
  name: string;
  description: string;
  duration: number;
  energy: 'low' | 'medium' | 'high';
}

// ============== CLIP ==============

export interface EditClip {
  id: string;
  source_video_id?: string;
  source_path: string;
  start_time: number;
  end_time: number;
  timeline_position: number;
  transition_in?: TransitionType;
  transition_in_duration: number;
  effects: Effect[];
  label?: string;
}

// ============== AUDIO ==============

export interface AudioTrack {
  source_path: string;
  duration: number;
  beats: number[];
  bpm?: number;
  volume: number;
}

// ============== EDIT PLAN ==============

export interface EditPlan {
  id: string;
  job_id: string;
  style: StyleType;
  audio: AudioTrack;
  clips: EditClip[];
  total_duration: number;
  created_at: string;
  updated_at: string;
  ai_model?: string;
  generation_prompt?: string;
  rendered: boolean;
  output_path?: string;
}

export interface EditPlanCreate {
  job_id: string;
  style: StyleType;
  target_duration: number;
  video_paths: string[];
  audio_path: string;
}

export interface EditPlanUpdate {
  clips?: EditClip[];
  audio?: AudioTrack;
  style?: StyleType;
}

export interface EditPlanResponse {
  success: boolean;
  plan?: EditPlan;
  message?: string;
}

export interface RenderRequest {
  plan_id: string;
  quality: RenderQuality;
  output_format?: 'mp4' | 'mov' | 'webm';
}

// ============== CATALOGS ==============

export interface EffectCatalog {
  [key: string]: EffectMeta;
}

export interface TransitionCatalog {
  [key: string]: TransitionMeta;
}

export interface StyleInfo {
  name: string;
  description: string;
  ai_prompt: string;
}

export interface StyleCatalog {
  [key: string]: StyleInfo;
}

// ============== UI STATE ==============

export interface TimelineState {
  currentTime: number;
  zoom: number;
  selectedClipId: string | null;
  isDragging: boolean;
}

export interface EditPlanState {
  plan: EditPlan | null;
  isLoading: boolean;
  isGenerating: boolean;
  isRendering: boolean;
  error: string | null;
  timeline: TimelineState;
  catalogs: {
    effects: EffectCatalog;
    transitions: TransitionCatalog;
    styles: StyleCatalog;
  };
}
