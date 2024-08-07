---
title: 0、java并发知识点
pubDate: 2024-01-01
categories: ['Java']
description: 0、java并发知识点
---

# HappensBefore 规则
1. 顺序性：一个线程中，前面的操作HappensBefore 后面的操作
2. volatile 变量规则 : 对于volatile 变量的写操作， HappendsBefore 对于该变量的读操作
3. 传递性规则 : 如果 A HappensBeofore B, B HappensBefore C ，那么 A HappensBefore C
4. sychronized 锁规则 : 对于一个锁的解锁操作 HappensBefore 对于该锁的加锁操作
5. start() 规则 : 主线程 A 中启动子线程 B 后， 子线程 B 中可以看见主线程在启动子线程 B 之前的操作。
6. join() 规则 : 主线程 A 等待子线程 B 的完成，子线程 B 完成后，主线程中可以看到子线程对于共享变量的操作。

## 死锁的必要条件
1. 互斥 : 共享资源 X 和 Y 只能被一个线程占用。
2. 占有且等待 : 某线程占有共享资源 X 且等待 Y 资源的释放，在等待 Y 资源的时候，不会主动释放
3. 不可抢占 : 其他线程不能抢占线程 T1 占用的资源。
4. 循环等待 : 线程 T1 等待线程 T2 占有的资源，同时线程 T2 等待线程 T1 占有的资源

## 死锁的预防：破坏四个死锁条件之一，就可以预防死锁。其中互斥条件是不能被打破的，因为我们使用锁就是为了互斥。
1. 破坏 占有且等待：一次性申请所有资源即可，单独包装一个类来做资源申请，如果两个资源都申请到了，就使用锁，如果只申请到一个，就释放已经申请到的这个锁给其他线程。
2. 破坏 不可抢占：sychronized 默认实现的管程，没有办法破坏不可抢占的条件，一旦 sychronized 锁获取到之后，不能被打断。使用Lock实现管程，可以破坏不可抢占条件：
- Lock.lockInterruptibly() 可以被interrupt 方法打断，抛出一个 InterruptedException 异常
- Lock.tryLock() 不会阻塞的获取锁，如果拿不到锁，直接返回一个 false 。
- Lock.tryLock(long time) 可以给定一个超时时常，如果超时后获取不到锁，直接返回一个 false。
3. 破坏 循环等待：申请锁的时候，按照一定顺序来申请，比如申请的是同一个类的两个对象的锁，那么可以给该类指定一个id，按照id从小到大来申请，可以避免循环等待。

## Java 线程的生命周期
- NEW
- RUNNABLE
- TERMINATED
- WAITING
- TIMED_WAITING
- BLOCKED

## Java 线程生命周期的互相转换
- NEW -> RUNNABLE : new Thread().start() , new Thread(Runnable run).start()
- RUNNABLE -> TERMINATED : 线程执行完 run() 方法后，会自动转到 TEMINATED 状态，如果线程 run() 的过程中抛出了异常，也会转到 TEMMINATED 状态。run() 方法执行过程中强行中断有两个方法：
	- 可以使用 stop() 不过该方法已经不推荐使用了，因为 stop() 之后，线程就直接杀死了，不会释放持有的锁，那么该锁也就永远没有办法被其他线程使用了。
	- 现在推荐使用 interrupt() 方法.
- RUNNABLE -> BLOCKED : 获取 sychronized 锁的时候，如果没有获取到，就会进入入口等待队列，转换为 BLOCKED 状态。当获取到锁之后，就会转回到 RUNNABLE 状态
- RUNNBALBE -> WAITING : 
	- Thread.join()
	- Object.wait()
	- LockSupport.park()
- RUNNABLE -> TIMED_WAITING : 
	- Thread.join(long time)
	- Thread.sleep(long millis)
	- Object.wait(long time)
	- LockSupport.parkUntil(long deadline)
	- LockSupport.parkNanos(Object blocker, long deadline)

## 创建多少线程才是最合适的？
1. CPU 密集型程序：1 + CPU 个数
2. I/O 密集型程序：CPU 个数 * (1 + I/O 耗时 / CPU 耗时) , 由于耗时不好计算，可以使用 2*CPU 个数 + 1 作为线程数的初始值，然后通过压测来测试最佳线程数。


## 并发程序的问题
- 微观来说：原子性、有序性、可见性
	- 原子性：如果不能保证原子性，那么指令 count++ 在并发的时候存在问题
	- 有序性：jvm 会在编译优化的时候进行指令重拍，有时候会出现一些意想不到的bug，比如双重检验锁做单例模式里面，如果单例不是volatile的，有可能出现空指针异常错误
	- 可见性：cpu 缓存导致的两个线程操作共享变量的时候出现不可见的情况
- 宏观来说：安全性、活跃性、性能
	- 安全性问题：都可以使用互斥锁的方案解决
		- 数据竞争问题：多个线程同时访问一个数据，并且至少有一个线程会写入该数据
		- 竞态条件问题：程序的执行结果依赖线程的执行顺序，从而导致了程序执行结果的不确定性。
	- 活跃性：死锁、活锁、饥饿
		- 死锁：破坏四个必要条件之一即可。
		- 活锁：相当于两个人一直互相谦让，就会一直撞到一起，那么在谦让的时候，等待一个随机时间就可以了。
		- 饥饿：某些线程一直拿不到锁，就会导致饥饿。可以使用公平锁来解决。Lock lock = new ReentrantLock(true)
	- 性能：使用并发就是为了减少串行增强性能，而加锁虽然能解决安全性问题，但是会增加串行程度，进而影响性能，所以要在必须加锁的地方加锁。
		- 使用无锁的算法和数据结构。比如	线程本地存储、写入时复制（copy-on-write）、乐观锁。java并发包里的原子类，Disruptor是一个无锁队列
		- 减少锁的持有时间。比如 读写锁，细粒度锁（concurrentHashMap,分段锁技术）


## 用锁的最佳实践
- 永远只在更新对象的成员变量时加锁
- 永远只在访问对象的可变成员变量时加锁
- 永远不在调用其他对象的方法时加锁

## Condition 的作用
Java 语言内置的管程里只有一个条件变量，而Lock&Condition实现的管程是支持多个条件变量。

## Semaphore 的作用
Semaphore 可以实现多个线程进入同一个临界区，可以用于实现对象池操作。
- 信号量模型：三个方法，一个等待队列，一个计数器。等待队列和计数器对外界是透明的。通过三个方法来做控制。
	- init() : 设置计数器的初始值
	- down() : 计数器的值减 1 ，如果此时计数器的值小于0，那么当前线程被阻塞，否则线程可以继续执行。
	- up() : 计数器的值加 1 ，如果此时计数器的值小于等于0，那么唤醒等待队列中的一个线程，并将其从等待队列移除。
- Java 中对于这三个方法的实现分别是：
	- Semaphore() 构造函数，可以传入一个计数器初始值
	- aquire() 是down() 方法的实现
	- release() 是 up() 方法的实现

## ReadWriteLock 特点
- 允许多个线程读共享变量，仅允许一个线程写共享变量，当一个写线程正在执行写操作的时候，此时禁止读线程读共享变量。
- ReadWriteLock 不允许锁升级，如果出现了读锁升级为写锁的代码，此时读锁尚未被释放，会导致写锁永久等待，最终导致其他相关线程都被阻塞，永远没有机会唤醒。
- 锁的降级是被允许的

### 缓存的初始化策略
- 数据量少的话，可以选择一次性加载
- 数据量多的话，可以考虑懒加载，也就是按需加载

### 缓存的数据同步策略
- 给缓存一个超时机制，存入缓存的数据并不是永久有效的，可以在超时之后，再从持久化的库里进行同步操作。
- 也可以在源头数据变化的时候，主动通知缓存更新数据。
- 也可以使用数据库和缓存双写策略。

## StampedLock 特点
- 支持写锁、悲观读锁和乐观读，需要注意的是乐观读(sl.tryOptimisticRead)并不是锁，所以也无需解锁操作。
	- sl.writeLock 返回 long stamp，在解锁时需要传入 sl.unLockWrite(stamp)
	- sl.readLock 返回 long stamp , 与写锁类似，在解锁时需要传入 sl.unLockRead(stamp)
	- 以上两个操作在阻塞过程中，不可以使用interrupt打断，否则会使cpu飙升至100%，如果需要打断操作，可以使用sl.readLockInterruptibly() 或者 sl.writeLockInterruptibly()
	- 使用乐观读的时候，需要判断在读期间是否有写操作，如果有写操作，需要手动升级为悲观读，并注意读完之后释放悲观读锁。即：long stamp = sl.tryOptimisticLock(); 读操作完成之后，校验在读的过程中是否有写操作，sl.validate(stamp) 如果返回 true，那么就没有过写操作，否则需要手动添加悲观锁，再次读。
- StampedLock 不支持重入。
- StampedLock 支持锁的降级和升级，通过 tryConvertToReadLock() 和 tryConvertToWriteLock() 实现


## CountDownLatch 特点
- 主要解决一个线程等待多个线程的场景，类似 导游 在景点等待 所有游客到齐之后，一起进景点。
- CountDownLatch 的计数器不能自动重置，是不可以循环利用的，当计数器变为 0 之后，再次调用 latch.await() 方法，会直接通过。

## CyclicBarrier 特点
- 主要解决多个线程之间相互等待的问题，类似 驴友们 提前约定好在某个位置等待，人到齐之后一起做某件事。
- 计数器到 0 之后会自动重置为创建计数器时设置的初始值，可以循环使用。
- CyclicBarrier 可以设置回调函数，使用更方便。

## 并发容器
### List
- CopyOnWriteArrayList : 

### Map
- ConcurrentHashMap
- ConcurrentSkipListMap

### Set
- CopyOnWriteArraySet
- ConcurrentSkipListSet

### Queue
- 单端阻塞队列 : 
	- 内部队列是数组：ArrayBlockingQueue
	- 内部队列是链表：LinkedBlockingQueue
	- 内部不持有队列：SynchronouseQueue, 生产者线程的入队操作必须等待消费者线程的出队操作
	- LinkedTransferQueue: 融合了 LinkedBlockingQueue 和 SynchronouseQueue 的功能，性能比LinkedBlockingQueue 更好
	- 支持按优先级出队：PriorityBlockingQueue 
	- 支持延时出队：DelayQueue
- 双端阻塞队列 : LinkedBlockingDeque
- 单端非阻塞队列 : ConcurrentLinkedQueue
- 双端非阻塞队列 : ConcurrentLinkedDeque

## CAS
- CAS指令中包含三个参数：共享变量的内存地址A、用于比较的值B和共享变量的新值C
- 作为一条CPU指令，CAS指令本身是能够保证原子性的

### CAS 中的 ABA 问题
- 问题描述：线程T1在执行 CAS 操作的时候，读到的是A，这个时候线程 T2 将其更新为了 B，同时线程 T3 将其更新成了 A，那么线程 T1 读到的依然是 A，但是这个时候 A 的属性可能已经发生了变化，线程 T1 却并不清楚。
- 问题解决：可以通过类似 MySQL 乐观锁的思路来解决，即增加一个版本号维度，每次执行 CAS 操作的时候，附加再更新一个版本号，只要保证版本号是递增的，那么即便 A 编程 B 又变回 A，版本号也不会变回来。

## java 并发包中的原子类
- 基本数据类型
	+ AtomicBoolean
	+ AtomicInteger
	+ AtomicLong
- 引用类型
	+ AtomicReference
	+ AtomicStampedReference
	+ AtomicMarkableReference
- 数组
	+ AtomicIntegerArray
	+ AtomicLongArray
	+ AtomicReferenceArray
- 对象属性更新器
	+ AtomicIntegerFieldUpdater
	+ AtomicLongFieldUpdater
	+ AtomicReferenceFieldUpdater
- 累加器
	+ DoubleAccumulator
	+ DoubleAdder
	+ LongAccumulator
	+ LongAdder

## Executor
### Java 并发类库中提供的线程池有哪几种？分别有什么特点？
- Executors 工具类提供了 5 种线程池
	+ newFixedThreadPool(int nThreads) : 使用的LinkedBlockingQueue(), 任何时候最多有 nThreads 个线程是活动的。如果任务数量超过了活动队列数目，就要到工作队列中等待空闲线程的出现。如果有工作线程退出，就会创建新的工作线程，补足指定数目的 nThreads;
	+ newCachedThreadPool(): 这是一种可以用来处理短时间内大量工作任务的线程池，内部队列使用的是 SychronouseQueue()。他会视图缓存线程并重用，当没有缓存线程可用的时候，会创建新的工作线程。如果线程闲置时间超过60秒，就会被终止并移除缓存；长时间限制时，这种线程池不会消耗什么资源。
	+ newSingleThreadExecutor(): 工作线程数目被限制为 1 ， 创建方式类似 newFixedThreadPool(1), 不过不同点是该线程池 不允许使用者改动该线程池实例，因此可以避免其改变线程数目。
	+ newSingleThreadScheduledExecutor() 和 newScheduledThreadPool(): 创建的是 ScheduledExecutorService, 可以进行定时或周期性的工作调度，两者区别在于 单一工作线程还是多个工作线程，内部是 DelayQueue。
	+ newWorkingStealingPool(int parallelism): 该方法创建的是 ForkJoinPool , 会利用线程窃取算法来提升线程利用率和工作效率，可以并行的处理任务，不保证处理顺序。

## Future

## CompletableFuture
- 该工具类提供了异步编程的基本方法，创建CompletableFuture 对象主要依赖 `runAsync` 和 `supplyAsync` 两个方法，这两个方法如果不传入线程池对象，则会使用公共的ForkJoinPoll 线程池
- CompletableFuture 实现了 CompletionStage 接口，主要有以下方法提供异步编程的支持
	- 串行方法 : `thenApply(Function fn);`  `thenAccept(Consumer consumer);`  `thenCompose(Function fn);`  `thenRun(Runnable action);`
	- 汇聚 ADD 方法 : `thenCombine(CompletionStage other, Function fn);` `thenAcceptBoth(CompletionStage other, Consumer consumer);` `runAfterReturn(CompletionStage other, Runnable action);`
	- 汇聚 OR 方法 : `applyEither(CompletionStage other, Function fn);` `acceptEither(CompletionStage other, Consumer consumer);` `runAfterEither(CompletionStage other, Runnable action);`
	- 异常处理方法 : `exceptionally(Function fn);` `whenComplete(Consumer consumer);` `handle(Function fu); `

## CompletionService
- CompetionService 内部有一个阻塞队列，可以将实现异步的将线程任务执行结果添加到阻塞队列中。
### 适用场景：
- 适合批量提交异步任务的场景，该类将线程池 Executor 和阻塞队列 BlockingQueue 的功能融合在一起，能够让批量异步任务的管理更简单。
- 除此之外，CompletionService 能够让异步任务执行结果有序化，先执行完的先进入阻塞队列，利用这个特性可以轻松处理后续操作，避免无谓的等待，同时可以快速实现 “多个线程异步启动，只要一个线程返回结果，那么就可以停止其他线程，执行后续操作” 的任务。

## 常见的并发设计模式

### 避免共享的设计模式
- Immutabilaty 模式 : `String`、`Long`、`Double`、`Integer` 都具有不可变性，这些基础类型的包装类都是靠不可变性来保证线程安全的。
	+ 如何快速实现具备不可变性的类 : 将一个类的所有属性都设置为final的，并且只允许存在只读方法，那么这类就是不可变性的了。更严格的做法是让这个类本身也是final的，也就是不允许继承。
- CopyOnWrite 模式 ： 适合“对性能要求高，读多写少，若一致性” 的场景。缺点是修改的时候非常消耗内存，每次修改都需要复制一个对象出来。
- 线程本地存储模式 ： 局部变量和 ThreadLocal 都可以做到避免共享。
	+ ThreadLocal : 同一个线程多次调用TreadLocal 的get() 方法，返回值是一样的，而不同线程调用返回值是不一样的，这样解决了线程变量的共享问题。
	+ ThreadLocal 的实现 : Thread 中有一个私有属性，threadLocals ，其类型是 ThreadLocalMap ，该 Map 的 key 是 ThreadLocal。
	+ 在线程池中使用过 ThreadLocal 有内存泄漏的风险：线程池中的线程存活时间太长，往往和程序是同生共死的，这就意味着Thread 持有的 ThreadLocalMap 一直都不会被回收，再加上 ThreadLocalMap 中的 Entry 对 ThreadLocal 是弱引用，所以只要 ThreadLocal 结束了自己的生命周期是可以被回收的。但是 Entry 中的 Value 确实被 Entry 强引用的，所以即便 Value 的生命周期结束了，Value 也是无法被回收的，从而导致内存泄漏。
	+ 如何解决线程池中的ThreadLocal 内存泄漏问题： 可以使用 try{} finanlly{tl.remove()} 进行手动释放。
	+ Spring 中的事务管理器是使用 ThreadLocal 来传递事务信息的，因此这个事务信息是不能跨线程共享的，所以不能在异步场景中使用 Spring 的事务管理器。

### 多线程版本 IF 的设计模式

- Guarded Suspension (保护性地暂停)模式: 这个是等待唤醒模式的规范实现, 该模式解决 if 问题会等待 if 条件为真。
	+ 实现结构：一个对象 GuardedObject, 内部有一个成员变量--受保护的对象，以及两个成员方法--get(Predicate<T> p) 和 onChanged(T obj) 方法。 其中，对象 GuardedObject 就是类似饭店的大堂经理，受保护的对象就类似餐厅的包间；受保护对象的 get() 方法就类似我们的就餐，就餐的前提是包间收拾好了，参数 p 就是用来描述这个前提条件的；受保护对象的 onChanged() 方法对应的就是服务员把包间收拾好了，通过 onChanged() 方法可以 fire 一个事件，而这个事件往往能改变前提条件 p 的计算结果。
- Balking 模式 : 使用该方法解决 if 问题，不需要等待，如果条件不满足，直接中断即可。

### 三种最简单的分工模式

- Thread-Per-Message 模式 : 委托他人办理的方式，在并发编程领域被总结为一种设计模式，叫做Thread-Per-Message模式，简言之就是为每个任务分配一个独立的线程。
- Worker Thread 模式 : Java 线程池的实现模式。类似车间里的工人，有活儿了大家一起干，没活儿了就聊聊天等着。能够避免重复创建、销毁线程，同时能够限制创建线程池的上限。
	+ 可能导致 OOM 的两个场景：
		* 无限制的创建线程：线程池可以通过给定线程上限来避免。
		* 无限制的接收任务：可以给定一个有界的工作队列。
	+ 注意：**提交到线程池中的任务一定要是相互独立的，否则有可能会出现死锁的风险**
- 生产者-消费者模式
- 优点
	+ 解耦
	+ 支持异步，平衡生产者与消费者的速度差异
	+ 支持批量执行以提升性能
		* 例如，我们要在数据库里INSERT 1000条数据，有两种方案：第一种方案是用1000个线程并发执行，每个线程INSERT一条数据；第二种方案是用1个线程，执行一个批量的SQL，一次性把1000条数据INSERT进去。这两种方案，显然是第二种方案效率更高，其实这样的应用场景就是我们上面提到的批量执行场景。
	+ 支持分阶段提交，以提升性能

## 两阶段终止模式
- 将线程终止分为两个阶段
	+ 第一个阶段：线程 T1 向线程 T2 发送终止指令
		* 想要终止一个线程，需要先使用 interrupt() 方法，把线程从休眠状态转化为 RUNNABLE 状态
	+ 第二个阶段：线程 T2 响应终止指令
		* RUNNABLE 状态转换到终止状态，优雅的方式是让 Java 线程自己执行完 run() 方法，所以我们一般采用的方法是 **设置一个标志位，然后线程会在何时的时机检查这个标志位，如果发现符合终止条件，则自动退出 run() 方法**
- 线程池的两个终止方法
	+ shutdown() : 只影响任务阻塞队列接收任务，执行中的任务不会被终止。
	+ shutdownNow() : 该方法会中断正在执行的线程。






























