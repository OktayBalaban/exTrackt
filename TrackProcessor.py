# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 19:30:44 2023

@author: oktay
"""

from spleeter.separator import Separator
from pydub import AudioSegment
import librosa
import numpy as np
import soundfile as sf

class TrackProcessor():
    def __init__(self):
        pass
        
        
    def separate(self, stem_count, input_path, output_directory):
        separator = Separator(f'spleeter:{stem_count}stems')
        separator.separate_to_file(input_path, output_directory)
        
    def merge(self, stems, output_directory, song_name):
        merged = None
    
        for stem in stems:
            stem_audio = AudioSegment.from_wav(f"{output_directory}/{song_name}/{stem}.wav")
            if merged is None:
                merged = stem_audio
            else:
                merged = merged.overlay(stem_audio)
    
        merged.export(f"{output_directory}/{song_name}/merged.wav", format='wav')
        
    def shift_pitch(self, input_path, output_path, semitones):
        # Load the audio file
        samples, sample_rate = librosa.load(input_path, sr=None)
    
        # Shift the pitch
        pitch_shifted_samples = librosa.effects.pitch_shift(samples, sample_rate, n_steps=semitones)
    
        # Write the pitch-shifted samples to the output file using soundfile library
        sf.write(output_path, pitch_shifted_samples, sample_rate, 'PCM_24')