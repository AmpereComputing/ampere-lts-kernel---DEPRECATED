--- a/trace_irqoff.c
+++ b/trace_irqoff.c
@@ -700,10 +700,18 @@ static const struct proc_ops enable_fops = {
        .proc_release   = single_release,
 };
 #endif
+#include <linux/delay.h>
+static void test_hardirq(int latency)
+{
+    local_irq_disable();
+    mdelay(latency);
+    local_irq_enable();
+}

 static int sampling_period_show(struct seq_file *m, void *ptr)
 {
        seq_printf(m, "%llums\n", sampling_period / (1000 * 1000UL));
+       test_hardirq(1000);

        return 0;
 }

cd /proc/trace_irqoff/
cat sampling_period

cat distribute
hardirq-off:
         msecs           : count     distribution
        10 -> 19         : 0        |                                        |
        20 -> 39         : 0        |                                        |
        40 -> 79         : 0        |                                        |
        80 -> 159        : 0        |                                        |
       160 -> 319        : 0        |                                        |
       320 -> 639        : 0        |                                        |
       640 -> 1279       : 1        |****************************************|
softirq-off:
         msecs           : count     distribution
        10 -> 19         : 477100   |****************************************|
        20 -> 39         : 14559    |*                                       |

cat trace_latency
trace_irqoff_latency: 50ms

 hardirq:
 cpu: 148
     COMMAND: cat PID: 35333 LATENCY: 995ms
     save_trace.isra.0+0x178/0x1c0 [trace_irqoff]
     trace_irqoff_record+0x100/0x110 [trace_irqoff]
     trace_irqoff_hrtimer_handler+0x58/0x138 [trace_irqoff]
     __hrtimer_run_queues+0x148/0x324
     hrtimer_interrupt+0xfc/0x270
     arch_timer_handler_phys+0x40/0x50
     handle_percpu_devid_irq+0x94/0x1c0
     handle_domain_irq+0x6c/0x9c
     gic_handle_irq+0xec/0x184
     call_on_irq_stack+0x2c/0x38
     do_interrupt_handler+0x5c/0x70
     el1_interrupt+0x30/0x50
     el1h_64_irq_handler+0x18/0x24
     el1h_64_irq+0x78/0x7c
     sampling_period_show+0x7c/0xbc [trace_irqoff]
     seq_read_iter+0x1dc/0x4f0
     seq_read+0xe4/0x140
     proc_reg_read+0xb4/0xf0
     vfs_read+0xb8/0x1f0
     ksys_read+0x74/0x100
     __arm64_sys_read+0x28/0x34
     invoke_syscall+0x50/0x120
     el0_svc_common.constprop.0+0x54/0x184
     do_el0_svc+0x34/0x9c
     el0_svc+0x30/0x100
     el0t_64_sync_handler+0xa4/0x130
     el0t_64_sync+0x1a0/0x1a4


 softirq:



