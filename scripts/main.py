import argparse
from hexlet_code.page_loader import PageLoader



def main():
    parser = argparse.ArgumentParser(description="Allows downloading webpages using url")
    parser.add_argument("src")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--log-cli-level", action="store_true", help="Log CLI level")
    args = parser.parse_args()
    pl = PageLoader()
    result = pl.download(page=args.src, save_dir=args.output, log_show=args.log_cli_level)
    print(result)

if __name__ == "__main__":
    main()