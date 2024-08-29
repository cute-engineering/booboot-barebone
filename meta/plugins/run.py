from cutekit import const, cli, model, shell, builder
from pathlib import Path


@cli.command("r", "run", "Run Booboot barebone")
def _(args: model.TargetArgs):
    target_spec = args.target
    if "host" in target_spec:
        target_spec = "kernel-x86_64"

    registry = model.Registry.use(args)
    component = registry.lookup("kernel", model.Component)
    if component is None:
        raise ValueError("Kernel not found")

    target = registry.lookup(target_spec, model.Target)
    if target is None:
        raise ValueError(f"Target not found: {target_spec}")

    scope = builder.TargetScope(registry, target)

    ck = Path(const.PROJECT_CK_DIR)
    meta = Path(const.META_DIR)
    (ck / "image").mkdir(exist_ok=True, parents=True)
    (ck / "image" / "efi" / "boot").mkdir(exist_ok=True, parents=True)

    shell.cp(
        shell.wget(
            "https://github.com/cute-engineering/booboot/releases/download/v0.1.0/bootx64.efi"
        ),
        str(ck / "image" / "efi" / "boot" / "bootx64.efi"),
    )

    products = builder.build(scope, component)
    shell.cp(str(products[0].path), str((ck / "image" / "kernel.elf")))

    shell.cp(
        str(meta / "res" / "booboot.tga"),
        str(ck / "image" / "booboot.tga"),
    )

    shell.cp(str(meta / "config" / "loader.json"), str(ck / "image" / "loader.json"))

    shell.exec(
        "qemu-system-x86_64",
        "-no-reboot",
        "-no-shutdown",
        "-smp",
        "4",
        "-debugcon",
        "mon:stdio",
        "-drive",
        f"format=raw,file=fat:rw:{ck / 'image'},media=disk",
        "-bios",
        shell.wget("https://retrage.github.io/edk2-nightly/bin/RELEASEX64_OVMF.fd"),
    )
