# Optimized Apollo Controller

## Better controller

The three files below are the optimized controller with better performance. There files are expected to replace the original files in [Apollo](https://github.com/ApolloAuto/apollo/tree/v8.0.0).

```
control_conf.pb.txt
mpc_controller.cc
mpc_controller.h
```

## Trajectory recorder

Particularly, the file _mpc\_controller\_MetricRecorder.cc_ is used to collect the planned and actual trajectories. This file is instrumented with code to record the necessary data. 

To use this data recorder, first replace the original MPC controller _mpc\_controller.cc_ with this dedicated _mpc\_controller\_MetricRecorder.cc_, then re-compile and re-run the control module.


