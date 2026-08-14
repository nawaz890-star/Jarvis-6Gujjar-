# Sample echo plugin
# This plugin reads JSON from stdin and echoes it back with a message.
import sys
import json

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.run:
        raw = sys.stdin.read()
        try:
            obj = json.loads(raw)
        except Exception:
            obj = {'error': 'invalid json'}
        resp = {'ok': True, 'echo': obj}
        print(json.dumps(resp))