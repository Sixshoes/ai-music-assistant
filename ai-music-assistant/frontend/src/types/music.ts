export type MusicGenre = 'pop' | 'rock' | 'jazz' | 'classical' | 'electronic' | 'folk' | 'hip_hop' | 'rnb' | 
                     'country' | 'blues' | 'ambient' | 'funk' | 'latin' | 'world';

export type MusicKey = 'C' | 'G' | 'D' | 'A' | 'E' | 'B' | 'F#' | 'C#' | 'F' | 'Bb' | 'Eb' | 'Ab' | 'Db' | 'Gb' | 'Cb' |
                    'Am' | 'Em' | 'Bm' | 'F#m' | 'C#m' | 'G#m' | 'D#m' | 'A#m' | 'Dm' | 'Gm' | 'Cm' | 'Fm' | 'Bbm' | 'Ebm' | 'Abm';

export type Instrument = 'piano' | 'guitar' | 'drums' | 'bass' | 'strings' | 'brass' | 'woodwinds' | 
                     'synth' | 'vocal' | 'organ' | 'percussion' | 'harp' | 'marimba' | 'accordion' |
                     'violin' | 'cello' | 'flute' | 'trumpet' | 'saxophone' | 'choir' | 'clarinet';

export type MusicMood = 'happy' | 'sad' | 'energetic' | 'calm' | 'romantic' | 'dark' | 'nostalgic' | 
                    'epic' | 'playful' | 'mysterious' | 'anxious' | 'hopeful' | 'dreamy' | 'angry';

export type MusicStyle = 'normal' | 'staccato' | 'legato' | 'arpeggio' | 'pizzicato' | 'tremolo' | 'glissando';

export type TimeSignature = '4/4' | '3/4' | '6/8' | '2/4' | '5/4' | '7/8' | '12/8' | '9/8' | '3/8';

export type MusicalForm = 'verse_chorus' | 'aba' | 'rondo' | 'through_composed' | 
                      'theme_variations' | 'sonata' | 'binary' | 'ternary';

export type CommandType = 'text_to_music' | 'melody_to_arrangement' | 'music_analysis' | 
                      'pitch_correction' | 'style_transfer' | 'improvisation';

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export type ModelType = 'magenta' | 'musicgen' | 'transformer' | 'lstm' | 'gan' | 'diffusion';

export interface MusicParameters {
  description?: string;
  duration?: number;
  tempo?: number;
  key?: MusicKey;
  time_signature?: TimeSignature;
  genre?: MusicGenre;
  instruments?: Instrument[];
  complexity?: number;
  mood?: MusicMood;
  style?: MusicStyle;
  form?: MusicalForm;
}

export interface Note {
  pitch: number;
  start_time: number;
  duration: number;
  velocity: number;
}

export interface MelodyInput {
  notes: Note[];
  tempo?: number;
}

export interface AudioInput {
  audio_data_url: string;
  format: string;
  sample_rate?: number;
}

export interface ChordProgression {
  chords: string[];
  durations: number[];
}

export interface MusicData {
  audio_data?: string;
  midi_data?: string;
  score_data?: {
    musicxml?: string;
    pdf?: string;
    svg?: string;
  };
  tracks?: Record<string, Note[]>;
  cover_image?: string;
}

export interface MusicCommand {
  command_type: string;
  text_input?: string;
  melody_input?: MelodyInput;
  audio_input?: AudioInput;
  parameters?: MusicParameters;
  model_preferences?: ModelType[];
}

export interface MusicAnalysis {
  key: MusicKey;
  chord_progression: ChordProgression;
  time_signature: TimeSignature;
  tempo: number;
  structure: Record<string, number[]>;
  harmony_issues?: string[];
  suggestions?: string[];
  complexity_analysis?: Record<string, any>;
  melody_patterns?: number[][];
  genre?: MusicGenre;
  instruments?: Instrument[];
  duration?: number;
  complexity?: number;
  mood?: MusicMood;
  style?: MusicStyle;
}

export interface MusicResult {
  command_id: string;
  status: string;
  music_data?: MusicData;
  analysis?: MusicAnalysis;
  error?: string;
  suggestions?: string[];
  models_used?: ModelType[];
  processing_time?: number;
}

export interface CommandResponse {
  message: string;
  command_id: string;
}

export interface CommandStatus {
  status: string;
  command_type?: string;
  error?: string;
  processing_time?: number;
  elapsed_time?: number;
} 