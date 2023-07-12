# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 19:30:44 2023

@author: oktay
"""


from spleeter.separator import Separator
from pydub import AudioSegment
import librosa
import soundfile as sf

class TrackProcessor():
    def __init__(self):
        pass
        
        
    def separate(self, input_path, output_directory):
        separator = Separator('spleeter:4stems')
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
        samples, sample_rate = librosa.load(input_path, sr=None)
        pitch_shifted_samples = librosa.effects.pitch_shift(y=samples, sr=sample_rate, n_steps=semitones)
        sf.write(output_path, pitch_shifted_samples, sample_rate, 'PCM_24')