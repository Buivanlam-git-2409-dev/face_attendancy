from argparse import ArgumentParser
from pathlib import Path
from ultralytics import YOLO


def main():
    parser = ArgumentParser(description='Train a custom YOLO face detector.')
    parser.add_argument('--data', default='face_dataset/face.yaml',
                        help='Path to YOLO dataset YAML file.')
    parser.add_argument('--model', default='yolov8n.pt',
                        help='Base YOLO model. yolov8n.pt is light and good for CPU/laptop demos.')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--device', default=None,
                        help='Example: 0 for GPU, cpu for CPU. Leave empty for auto.')
    parser.add_argument('--project', default='runs/detect')
    parser.add_argument('--name', default='face_detector')
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(
            f'Dataset YAML not found: {data_path}\n'
            'Create it from face_dataset/face.yaml example first.'
        )

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
    )

    print('\nTraining finished.')
    print(f'Best model should be at: {args.project}/{args.name}/weights/best.pt')
    print('Copy it to: face_model/best.pt')


if __name__ == '__main__':
    main()
