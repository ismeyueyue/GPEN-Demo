import os
from os import path as osp

def scandir(dir_path, suffix=None, recursive=False, full_path=False):
    """Scan a directory to find the interested files.

    Args:
        dir_path (str): Path of the directory.
        suffix (str | tuple(str), optional): File suffix that we are
            interested in. Default: None.
        recursive (bool, optional): If set to True, recursively scan the
            directory. Default: False.
        full_path (bool, optional): If set to True, include the dir_path.
            Default: False.

    Returns:
        A generator for all the interested files with relative paths.
    """

    if (suffix is not None) and not isinstance(suffix, (str, tuple)):
        raise TypeError('"suffix" must be a string or tuple of strings')

    root = dir_path

    def _scandir(dir_path, suffix, recursive):
        for entry in os.scandir(dir_path):
            if not entry.name.startswith('.') and entry.is_file():
                if full_path:
                    return_path = entry.path
                else:
                    return_path = osp.relpath(entry.path, root)

                if suffix is None:
                    yield return_path
                elif return_path.endswith(suffix):
                    yield return_path
            else:
                if recursive:
                    yield from _scandir(entry.path, suffix=suffix, recursive=recursive)
                else:
                    continue

    return _scandir(dir_path, suffix=suffix, recursive=recursive)

def paired_paths_from_folder(folders, keys):
    """Generate paired paths from folders.

    Args:
        folders (list[str]): A list of folder path. The order of list should
            be [input_folder, gt_folder].
        keys (list[str]): A list of keys identifying folders. The order should
            be in consistent with folders, e.g., ['lq', 'gt'].
    Returns:
        list[str]: Returned path list.
    """
    assert len(folders) == 2, ('The len of folders should be 2 with [input_folder, gt_folder]. '
                               f'But got {len(folders)}')
    assert len(keys) == 2, f'The len of keys should be 2 with [input_key, gt_key]. But got {len(keys)}'
    input_folder, gt_folder = folders
    input_key, gt_key = keys

    input_paths = list(scandir(input_folder, recursive=True))
    gt_paths = list(scandir(gt_folder, recursive=True))
	
    # assert len(input_paths) == len(gt_paths), (f'{input_key} and {gt_key} datasets have different number of images: '
    #                                            f'{len(input_paths)}, {len(gt_paths)}.')
    paths = []
    for gt_path in gt_paths:
        input_name = osp.basename(gt_path)
        if input_name in input_paths:
            input_path = osp.join(input_folder, input_name)
            gt_path = osp.join(gt_folder, gt_path)
            paths.append(dict([(f'{input_key}_path', input_path), (f'{gt_key}_path', gt_path)]))

        # input_path = osp.join(input_folder, input_name)
        # assert input_name in input_paths, f'{input_name} is not in {input_key}_paths.'
        # gt_path = osp.join(gt_folder, gt_path)
        # paths.append(dict([(f'{input_key}_path', input_path), (f'{gt_key}_path', gt_path)]))
    return paths