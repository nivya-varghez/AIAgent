import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path("deployment_state")


def write_state(operation: str, payload: dict) -> Path:
    STATE_DIR.mkdir(exist_ok=True)
    target = STATE_DIR / f"{payload['app_name']}-{payload['environment']}-{operation}.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def deploy(args: argparse.Namespace) -> int:
    payload = {
        "operation": "deploy",
        "app_name": args.app_name,
        "environment": args.environment,
        "image_repository": args.image_repository,
        "version": args.version,
        "container_port": args.container_port,
        "release_reason": args.release_reason,
        "requested_by": args.requested_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deploy_command": args.deploy_command,
    }
    target = write_state("deploy", payload)
    print(f"Recorded deployment manifest at {target}")
    print(f"Deploy {args.image_repository}:{args.version} to {args.environment}")
    if args.deploy_command:
        print(f"Custom deploy command: {args.deploy_command}")
    return 0


def promote(args: argparse.Namespace) -> int:
    payload = {
        "operation": "promote",
        "app_name": args.app_name,
        "environment": args.target_env,
        "source_environment": args.source_env,
        "target_environment": args.target_env,
        "image_repository": args.image_repository,
        "version": args.version,
        "promotion_notes": args.promotion_notes,
        "requested_by": args.requested_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "promote_command": args.promote_command,
    }
    target = write_state("promote", payload)
    print(f"Recorded promotion manifest at {target}")
    print(f"Promote {args.image_repository}:{args.version} from {args.source_env} to {args.target_env}")
    if args.promote_command:
        print(f"Custom promote command: {args.promote_command}")
    return 0


def rollback(args: argparse.Namespace) -> int:
    payload = {
        "operation": "rollback",
        "app_name": args.app_name,
        "environment": args.environment,
        "image_repository": args.image_repository,
        "previous_version": args.previous_version,
        "incident_reference": args.incident_reference,
        "requested_by": args.requested_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rollback_command": args.rollback_command,
    }
    target = write_state("rollback", payload)
    print(f"Recorded rollback manifest at {target}")
    print(f"Rollback {args.image_repository} in {args.environment} to {args.previous_version}")
    if args.rollback_command:
        print(f"Custom rollback command: {args.rollback_command}")
    return 0


parser = argparse.ArgumentParser(description="Generic deployment workflow helper")
subparsers = parser.add_subparsers(dest="operation", required=True)

common = argparse.ArgumentParser(add_help=False)
common.add_argument("--app-name", required=True)
common.add_argument("--image-repository", required=True)
common.add_argument("--requested-by", required=True)

parser_deploy = subparsers.add_parser("deploy", parents=[common])
parser_deploy.add_argument("--environment", required=True)
parser_deploy.add_argument("--version", required=True)
parser_deploy.add_argument("--container-port", required=True)
parser_deploy.add_argument("--release-reason", default="")
parser_deploy.add_argument("--deploy-command", default="")
parser_deploy.set_defaults(func=deploy)

parser_promote = subparsers.add_parser("promote", parents=[common])
parser_promote.add_argument("--source-env", required=True)
parser_promote.add_argument("--target-env", required=True)
parser_promote.add_argument("--version", required=True)
parser_promote.add_argument("--promotion-notes", default="")
parser_promote.add_argument("--promote-command", default="")
parser_promote.set_defaults(func=promote)

parser_rollback = subparsers.add_parser("rollback", parents=[common])
parser_rollback.add_argument("--environment", required=True)
parser_rollback.add_argument("--previous-version", required=True)
parser_rollback.add_argument("--incident-reference", default="")
parser_rollback.add_argument("--rollback-command", default="")
parser_rollback.set_defaults(func=rollback)


if __name__ == "__main__":
    args = parser.parse_args()
    raise SystemExit(args.func(args))
