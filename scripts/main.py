import argparse
from hexlet_code.page_loader import PageLoader



def main():
    parser = argparse.ArgumentParser(description="Allows downloading webpages using url")
    parser.add_argument("src")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()
    pl = PageLoader()
    result = pl.download(page=args.src, save_dir=args.output)
    print(result)

if __name__ == "__main__":
    main()