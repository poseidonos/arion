import lib


def setup(id, pw, ip, huge_even_alloc, nrhuge, spdk_dir):
    lib.printer.green(f" + {__name__}.setup : {huge_even_alloc} {nrhuge}")
    run_setup = f"sshpass -p {pw} ssh -o StrictHostKeyChecking=no {id}@{ip} \
        sudo HUGE_EVEN_ALLOC={huge_even_alloc} NRHUGE={nrhuge} \
        {spdk_dir}/scripts/setup.sh"
    lib.subproc.sync_run(run_setup)
