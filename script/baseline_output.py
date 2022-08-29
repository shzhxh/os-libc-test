serial_out = r"""
"test_lua.sh" 9L, 190B written
root@debian:~/testsuits-for-oskernel/scripts/lua# chmod +x test_lua.sh 
root@debian:~/testsuits-for-oskernel/scripts/lua# ./test_lua.sh 
testcase lua date.lua success
testcase lua file_io.lua success
testcase lua max_min.lua fail 
testcase lua random.lua success
testcase lua remove.lua success
testcase lua round_num.lua fail
testcase lua sin30.lua success
testcase lua sort.lua success
testcase lua strings.lua success
  111 root      0:00 [ext4-rsv-conver]
  114 root      0:00 [kworker/u2:2-ex]
  144 root      0:01 /lib/systemd/systemd-journald
  158 root      0:00 /lib/systemd/systemd-udevd
  171 systemd-  0:00 /lib/systemd/systemd-timesyncd
  174 root      0:00 [hwrng]
  186 root      0:00 /usr/sbin/cron -f
  191 root      0:00 /usr/sbin/rsyslogd -n -iNONE
  214 root      0:00 [kworker/0:2-eve]
  217 root      0:00 /sbin/agetty -o -p -- \u --noclear tty1 linux
  218 root      0:00 /sbin/agetty -o -p -- \u --noclear tty2 linux
  219 root      0:00 /sbin/agetty -o -p -- \u --noclear tty3 linux
  220 root      0:00 /sbin/agetty -o -p -- \u --noclear tty4 linux
  221 root      0:00 /sbin/agetty -o -p -- \u --noclear tty5 linux
  222 root      0:00 /sbin/agetty -o -p -- \u --noclear tty6 linux
  223 root      0:00 /bin/login -p --
  224 root      0:00 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
  251 root      0:01 -bash
  479 root      0:00 [kworker/u2:1-ex]
  
testcase busybox ash -c exit success
testcase busybox sh -c exit success
bbb
testcase busybox basename /aaa/bbb success
     June 2021
Su Mo Tu We Th Fr Sa
       1  2  3  4  5
 6  7  8  9 10 11 12
13 14 15 16 17 18 19
20 21 22 23 24 25 26
27 28 29 30
                     
testcase busybox cal success
testcase busybox touch abc success
"hello world" > abc
testcase busybox echo "hello world" > abc success
echo "hello world" > abc
grep hello busybox_cmd.txt
testcase busybox grep hello busybox_cmd.txt success
testcase busybox cat abc success

testcase busybox clear success
testcase busybox cp busybox busybox_bak success
testcase busybox cut -c 3 abc success
0000000
testcase busybox od abc success
testcase busybox rm busybox_bak success
Mon Jun 21 02:28:58 UTC 2021
testcase busybox date success
Filesystem           1K-blocks      Used Available Use% Mounted on
udev                    443976         0    443976   0% /dev
tmpfs                    94468       188     94280   0% /run
/dev/vda1             10218644   1961304   7716676  20% /
tmpfs                   472336         0    472336   0% /dev/shm
tmpfs                     5120         0      5120   0% /run/lock
testcase busybox df success
/aaa
testcase busybox dirname /aaa/bbb success

testcase busybox dmesg success
1108	.
testcase busybox du success
"abc"
testcase busybox echo "abc" success
2
testcase busybox expr 1 + 1 success
testcase busybox false success
testcase busybox true success
testcase busybox find -name "busybox" success
              total        used        free      shared  buff/cache   available
Mem:         944672       42280      782572         188      119820      887144
Swap:             0           0           0
testcase busybox free success
testcase busybox head abc success
testcase busybox tail abc success
testcase busybox hexdump -C abc success
hwclock: can't open '/dev/misc/rtc': No such file or directory
testcase busybox hwclock fail
testcase busybox kill 10 success
abc                  busybox_cmd.txt      result.txt
busybox              busybox_testcode.sh
testcase busybox ls success
d41d8cd98f00b204e9800998ecf8427e  abc
testcase busybox md5sum abc success
testcase busybox mkdir test_dir success
testcase busybox mv test_dir test success
testcase busybox rmdir test success
"abcn"testcase busybox printf "abcn" success
PID   USER     TIME  COMMAND
    1 root      0:09 {systemd} /sbin/init noquiet
    2 root      0:00 [kthreadd]
    3 root      0:00 [rcu_gp]
  589 root      0:00 ./busybox ps
testcase busybox ps success
/root/testsuits-for-oskernel/scripts/busybox
testcase busybox pwd success
testcase busybox sleep 1 success
"aaaaaaa" >> abc
testcase busybox echo "aaaaaaa" >> abc success
"bbbbbbb" >> abc
testcase busybox echo "bbbbbbb" >> abc success
"ccccccc" >> abc
testcase busybox echo "ccccccc" >> abc success
"1111111" >> abc
testcase busybox echo "1111111" >> abc success
"2222222" >> abc
testcase busybox echo "2222222" >> abc success
sort: |: No such file or directory
testcase busybox sort abc | uniq fail
  File: abc
  Size: 0         	Blocks: 0          IO Block: 4096   regular empty file
Device: fe01h/65025d	Inode: 272553      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2021-06-21 02:28:58.623019297 +0000
Modify: 2021-06-21 02:28:58.559019951 +0000
Change: 2021-06-21 02:28:58.559019951 +0000
testcase busybox stat abc success
testcase busybox strings abc success
Linux
testcase busybox uname success
 02:29:00 up 26 min,  0 users,  load average: 0.00, 0.00, 0.00
testcase busybox uptime success
        0         0         0 abc
testcase busybox wc abc success
/bin/ls
testcase busybox which ls success
testcase busybox [ -f abc ] success
testcase busybox more abc success
testcase busybox rm abc success
If the CMD runs incorrectly, return value will put in result.txt
Else nothing will put in result.txt

TEST START
return: 1, cmd: hwclock
return: 2, cmd: sort abc | uniq
TEST END


latency measurements
Simple syscall: 0.3969 microseconds
Simple read: 0.9958 microseconds
Simple write: 0.6855 microseconds
mkdir: cannot create directory ‘/var/tmp’: File exists
Simple stat: 6.3198 microseconds
Simple fstat: 0.9349 microseconds
Simple open/close: 19.3684 microseconds
Select on 100 fd's: 10.2226 microseconds
Signal handler installation: 1.0861 microseconds
Signal handler overhead: 7.5202 microseconds
Pipe latency: 40.6122 microseconds
Process fork+exit: 1770.7500 microseconds
Process fork+execve: 2004.3333 microseconds
Process fork+/bin/sh -c: 12740.0000 microseconds
File /var/tmp/XXX write bandwidth:5617 KB/sec
Pagefaults on /var/tmp/XXX: 3.8195 microseconds
0.524288 161
file system latency
0k      30      5331    5777
1k      19      3514    4606
4k      18      3474    4557
10k     14      2551    4236
Bandwidth measurements
Pipe bandwidth: 266.12 MB/sec
0.524288 495.39
0.524288 458.86
0.524288 2069.56
0.524288 558.64
context switch overhead
"size=32k ovr=32.98
2 23.23
4 29.14
8 29.14
16 28.91
24 29.45
32 29.09
64 28.84
96 29.18
    """