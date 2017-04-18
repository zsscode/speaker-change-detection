import os
import sys

sys.path.append(os.path.abspath('..'))
from constants import c

import numpy as np

sys.path.append(os.path.abspath('..'))

from audio.audio_reader import AudioReader, extract_speaker_id
from audio.speech_features import get_mfcc_features_390


def generate_features(audio_entities, max_count):
    count = 0
    features = []
    while count < max_count:
        audio_entity = np.random.choice(audio_entities)
        voice_only_signal = audio_entity['audio_voice_only']
        cuts = np.random.uniform(low=1, high=len(voice_only_signal), size=2)
        signal_to_process = voice_only_signal[int(min(cuts)):int(max(cuts))]
        features_per_conv = get_mfcc_features_390(signal_to_process, c.AUDIO.SAMPLE_RATE, max_frames=None)
        if len(features_per_conv) > 0:
            features.append(features_per_conv)
        count += 1
    return features


def normalize(list_matrices, mean, std):
    return [(m - mean) / std for m in list_matrices]


def generate_data(max_count_per_class=500):
    # os.system('rm -rf /tmp/speaker-change-detection/')
    # os.system('mkdir /tmp/speaker-change-detection/')
    output = dict()
    audio = AudioReader(audio_dir=c.AUDIO.VCTK_CORPUS_PATH,
                        sample_rate=c.AUDIO.SAMPLE_RATE,
                        speakers_sub_list=None)
    print(audio.get_speaker_list())

    per_speaker_dict = dict()
    for filename, audio_entity in audio.cache.items():
        speaker_id = extract_speaker_id(audio_entity['filename'])
        if speaker_id not in per_speaker_dict:
            per_speaker_dict[speaker_id] = []
        per_speaker_dict[speaker_id].append(audio_entity)

    for speaker_id, audio_entities in per_speaker_dict.items():
        print('speaker id = {}'.format(speaker_id))
        cutoff = int(len(audio_entities) * 0.8)
        audio_entities_train = audio_entities[0:cutoff]
        audio_entities_test = audio_entities[cutoff:]

        print('processing {} speaker'.format(speaker_id))
        train = generate_features(audio_entities_train, max_count_per_class)
        print('processed {} for train/'.format(max_count_per_class))
        test = generate_features(audio_entities_test, max_count_per_class)
        print('processed {} for test/'.format(max_count_per_class))

        mean_train = np.mean([np.mean(t) for t in train])
        std_train = np.mean([np.std(t) for t in train])

        train = normalize(train, mean_train, std_train)
        test = normalize(test, mean_train, std_train)
        inputs = {'train': train,
                  'test': test,
                  'speaker_id': speaker_id}
        output[speaker_id] = inputs
    return output


if __name__ == '__main__':
    generate_data()
