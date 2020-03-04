# Benchmark results

## Number of tested algorithms: 4
## Number of test sets: 3

Test set 1: Low resolution

Test set 2: Medium resolution (720p)

Test set 3: High resolution (1080p)

### Average runtime (in seconds)
Algorithm \ Test Set | Low Res | Med Res | High Res
---|---|---|---
gamma|                  0.016|                  0.040|                  0.074
hdr_wls|                  3.809|                 14.795|                 22.309
hdr_adiff|                  0.748|                  2.363|                  3.492
hdr_bilat|                  0.297|                  0.735|                  0.982
hdr_cpp|                  0.303|                  0.503|                  0.792
hdr_cpp_const_O3|                  0.224|                  0.361|                  0.503


### Average size (% of original image)
Algorithm \ Test Set | Low Res | Med Res | High Res
---|---|---|---
gamma|                100.925|                 99.871|                 98.658
hdr_wls|                220.763|                239.487|                241.812
hdr_adiff|                255.952|                262.786|                266.111
hdr_bilat|                237.761|                229.334|                258.443
hdr_cpp|                222.011|                235.568|                233.932
