<template>
  <div>
    <input
      type="file"
      id="dicom_files"
      multiple="multiplt"
      placeholder="本地dicom文件上传"
    />
    <visible-show v-bind:dcms="dcms"> </visible-show>
  </div>
</template>
<script>
import VisibleShow from './VisibleShow.vue';

export default {
  name: "VisiblePage",
  components: {
    VisibleShow
  },
  data() {
    return {
      dcms:"",
    };
  },
  created() {
  },
  mounted() {
    // this.matting_ons = new Array([false,false,false]);

    document
      .getElementById("dicom_files")
      .addEventListener("change", this.handleFileSelect);
    
  },

  methods: {
    
    handleFileSelect(evt) {
    
      // console.log(1);
      evt.stopPropagation();
      evt.preventDefault();
      this.dcms = evt.target.files;
      // const dicom = evt.target.files[0];
      // this.imgs = new Array(this.dicoms0.length);
    },
   
  },
  computed: {
    // result_fusion_states:{
    //   get:function(){
    //     if(new_fusion == 1){
    //       return new Array([0,1,1,0]);
    //     }
    //     else if(new_fusion == 0){
    //       return new Array([-1,-1,-1,-1]);
    //     }
    //   }
    // }
  },
  watch: {
    dcms(n_d) {
        console.log(n_d)
      // console.log(n_d);
    },
  }
};
</script>
