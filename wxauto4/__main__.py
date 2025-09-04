import argparse
from .utils.useful import (
    authenticate,
    authenticate_with_file,
    get_licence_file,
    debug_license
)

def main():
    parser = argparse.ArgumentParser(description="wxauto plus V2命令行工具")
    parser.add_argument('--auth', '-a', type=str, help='使用wxauto plus V2的授权码进行授权')
    parser.add_argument('--auth-file', '-f', type=str, help='使用wxauto plus V2的授权文件进行授权')
    parser.add_argument('--export', '-e', action='store_true', help='导出wxauto plus V2的授权文件，发给管理员授权')
    parser.add_argument('--debug-license', '-d', action='store_true', help='导出wxauto plus V2的DEBUG授权文件，发给管理员授权')
    args = parser.parse_args()

    if args.auth:
        authenticate(args.auth)
    elif args.auth_file:
        authenticate_with_file(args.auth_file)
    elif args.export:
        get_licence_file()
    elif args.debug_license:
        debug_license()

if __name__ == '__main__':
    main()
