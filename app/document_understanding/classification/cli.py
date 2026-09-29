from pathlib import Path

from app.document_understanding.classification.gemini_classifier import ( GeminiDocumentClassifier,
                                                                          )

def main()->None:
    print("=" *50)
    print(" ADVO Document Classification")
    print("=" *50)

    image_path = input("Enter document path: ").strip()

    if not image_path:

        print("No document path provided.")
        return

    path = Path(image_path)

    if not path.is_file():
        print(f"File not found: {path}")
        return

    print("\nClassifying documents...\n")

    classifier = GeminiDocumentClassifier()
    result = classifier.classify(path)

    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()