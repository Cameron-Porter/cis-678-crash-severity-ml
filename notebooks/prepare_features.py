import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import notebook_root
from src.features.prepare import load_feature_split, save_feature_artifacts
from src.features.preprocessing import make_preprocessor


if __name__ == '__main__':
    root = notebook_root()
    frames, targets, exclusions = {}, {}, {}
    for split in ('train', 'validation'):
        frames[split], targets[split], exclusions[split] = load_feature_split(root, split)
    for configuration in ('core', 'expanded'):
        preprocessor = make_preprocessor(configuration)
        matrices = {'train': preprocessor.fit_transform(frames['train'])}
        matrices['validation'] = preprocessor.transform(frames['validation'])
        save_feature_artifacts(root, configuration, preprocessor, frames, targets, matrices, exclusions)
        print(configuration, {name: matrix.shape for name, matrix in matrices.items()}, flush=True)
