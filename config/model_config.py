MODEL_CONFIG = {
    # 人脸识别模型
    'face_recognition': {
        'shape_predictor': {
            'name': 'shape_predictor_68_face_landmarks.dat',
            'url': 'https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2',
            'path': 'models/face/shape_predictor_68_face_landmarks.dat'
        },
        'face_recognition': {
            'name': 'dlib_face_recognition_resnet_model_v1.dat',
            'url': 'https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2',
            'path': 'models/face/dlib_face_recognition_resnet_model_v1.dat'
        }
    },
    
    # 行为检测模型
    'behavior_detection': {
        'fall_detection': {
            'name': 'fall_detection_model.pth',
            'url': 'your_model_url',  # 需要配置自己的模型URL
            'path': 'models/behavior/fall_detection_model.pth'
        },
        'pose_estimation': {
            'name': 'pose_estimation_model.pth',
            'url': 'your_model_url',  # 需要配置自己的模型URL
            'path': 'models/behavior/pose_estimation_model.pth'
        }
    },
    
    # 语音模型
    'voice': {
        'wake_word': {
            'name': 'snowboy_model.pmdl',
            'url': 'your_model_url',  # 需要配置自己的模型URL
            'path': 'models/voice/snowboy_model.pmdl'
        }
    }
}

# 模型目录结构
MODEL_DIRS = [
    'models/face',
    'models/behavior',
    'models/voice',
    'models/temp'
]
