#/bin/bash

# cd ./bilateral_kernels
# ./bilateral_kernels.sh
# cd ../

scenes=( "data_Arcade" "data_BistroExterior" "data_BistroExterior2" "data_Classroom" "data_Dining-room" "data_Dining-room-dynamic" "data_Staircase" )
num_frames=(103 103 103 603 103 141 453)

# Iterate scenes and frames
for scene in "${scenes[@]}"; do
   frames=${num_frames[$scene]}
   echo "Processing scene: $scene, total frame: $frames"
   for ((i=0; i<frames; i++)); do
      python network_test.py -s test_Falcor -r /dataset_falcor -d $scene -ts $frames -t $i --export_exr
      mkdir -p output/$scene
      mv results/$scene/result/test_out/* output/$scene
   done
done

# python network_test.py -s test -r ./dataset -d classroom --export_exr -ts 60 -t 0