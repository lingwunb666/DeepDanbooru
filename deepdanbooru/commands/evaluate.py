import os

import tensorflow as tf

import deepdanbooru as dd


def evaluate(target_paths, project_path, model_path, tags_path, threshold, allow_gpu, compile_model, verbose):
    if not allow_gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

    if not model_path and not project_path:
        raise Exception('You must provide project path or model path.')

    if not tags_path and not project_path:
        raise Exception('You must provide project path or tags path.')

    target_image_paths = []

    for target_path in target_paths:
        if os.path.isfile(target_path):
            target_image_paths.append(target_path)
        else:
            target_image_paths.extend(dd.io.get_image_file_paths_recursive(target_path))

    target_image_paths = dd.extra.natural_sorted(target_image_paths)

    if model_path:
        if verbose:
            print(f'Loading model from {model_path} ...')
        model = tf.keras.models.load_model(model_path, compile=compile_model)
    else:
        if verbose:
            print(f'Loading model from project {project_path} ...')
        model = dd.project.load_model_from_project(project_path, compile_model=compile_model)

    if tags_path:
        if verbose:
            print(f'Loading tags from {tags_path} ...')
        tags = dd.data.load_tags(tags_path)
    else:
        if verbose:
            print(f'Loading tags from project {project_path} ...')
        tags = dd.project.load_tags_from_project(project_path)

    width = model.input_shape[2]
    height = model.input_shape[1]

    for image_path in target_image_paths:
        image = dd.data.load_image_for_evaluate(
            image_path, width=width, height=height)

        image_shape = image.shape
        image = image.reshape(
            (1, image_shape[0], image_shape[1], image_shape[2]))
        y = model.predict(image)[0]

        result_dict = {}

        for i, tag in enumerate(tags):
            result_dict[tag] = y[i]

        print(f'Tags of {image_path}:')
        for tag in tags:
            if result_dict[tag] >= threshold:
                print(f'({result_dict[tag]:05.3f}) {tag}')

        print()