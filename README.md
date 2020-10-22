# reproducer_bootstrap
## DESCRIPTION
## USAGE
## CONFIGURATION
## STRANGE ERRORS

### When deploying (still in trusted env)

Sometime the swap configuraiton fails on one of the node, how can this
be, as all nodes should be the same ? I haven't find the solution to
that one. Nodepool will fail and retry automatically. So until this
happen too often, I let it be.


    2020-10-11 22:34:17.310211 | LOOP [configure-swap : Remove any existing partitions]
    2020-10-11 22:34:17.637759 | secondary-1 | ERROR: Item: {'num': 1, 'begin': 0.0, 'end': 20480.0, 'size': 20480.0, 'fstype': 'fat32', 'name': '', 'flags': [], 'unit': 'mib'}
    2020-10-11 22:34:17.638372 | secondary-1 | {
    2020-10-11 22:34:17.638451 | secondary-1 |   "ansible_loop_var": "item",
    2020-10-11 22:34:17.638481 | secondary-1 |   "err": "Warning: Partition /dev/vdb is being used. Are you sure you want to continue?\n",
    2020-10-11 22:34:17.638507 | secondary-1 |   "item": {
    2020-10-11 22:34:17.638538 | secondary-1 |     "begin": 0.0,
    2020-10-11 22:34:17.638562 | secondary-1 |     "end": 20480.0,
    2020-10-11 22:34:17.638584 | secondary-1 |     "flags": [],
    2020-10-11 22:34:17.638607 | secondary-1 |     "fstype": "fat32",
    2020-10-11 22:34:17.638629 | secondary-1 |     "name": "",
    2020-10-11 22:34:17.638651 | secondary-1 |     "num": 1,
    2020-10-11 22:34:17.638674 | secondary-1 |     "size": 20480.0,
    2020-10-11 22:34:17.638697 | secondary-1 |     "unit": "mib"
    2020-10-11 22:34:17.638719 | secondary-1 |   },
    2020-10-11 22:34:17.638741 | secondary-1 |   "msg": "Error while running parted script: /sbin/parted -s -m -a optimal /dev/vdb -- rm 1",
    2020-10-11 22:34:17.638763 | secondary-1 |   "out": "",
    2020-10-11 22:34:17.638784 | secondary-1 |   "rc": 1
    2020-10-11 22:34:17.638806 | secondary-1 | }
    2020-10-11 22:34:17.638860 | secondary-1 | ok: All items complete
    2020-10-11 22:34:17.638885 | 
    2020-10-11 22:34:17.689321 | primary | changed:
    2020-10-11 22:34:17.689508 | primary | {
    2020-10-11 22:34:17.689548 | primary |   "begin": 0.0,
    2020-10-11 22:34:17.689578 | primary |   "end": 20480.0,
    2020-10-11 22:34:17.689606 | primary |   "flags": [],
    2020-10-11 22:34:17.689633 | primary |   "fstype": "fat32",
    2020-10-11 22:34:17.689660 | primary |   "name": "",
    2020-10-11 22:34:17.689686 | primary |   "num": 1,
    2020-10-11 22:34:17.689711 | primary |   "size": 20480.0,
    2020-10-11 22:34:17.689737 | primary |   "unit": "mib"
    2020-10-11 22:34:17.689763 | primary | }
    2020-10-11 22:34:17.689802 | primary | ERROR: All items complete
    2020-10-11 22:34:17.689827 | 
    2020-10-11 22:34:17.728175 | secondary-3 | changed:
    2020-10-11 22:34:17.728824 | secondary-3 | {
    2020-10-11 22:34:17.728975 | secondary-3 |   "begin": 0.0,
    2020-10-11 22:34:17.729018 | secondary-3 |   "end": 20480.0,
    2020-10-11 22:34:17.729048 | secondary-3 |   "flags": [],
    2020-10-11 22:34:17.729076 | secondary-3 |   "fstype": "fat32",
    2020-10-11 22:34:17.729103 | secondary-3 |   "name": "",
    2020-10-11 22:34:17.729130 | secondary-3 |   "num": 1,
    2020-10-11 22:34:17.729156 | secondary-3 |   "size": 20480.0,
    2020-10-11 22:34:17.729183 | secondary-3 |   "unit": "mib"
    2020-10-11 22:34:17.729210 | secondary-3 | }
    2020-10-11 22:34:17.760644 | secondary-2 | changed:
