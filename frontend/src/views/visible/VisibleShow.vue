<template>
  <div>
    <el-container>
      <el-header style="height: auto">
        <h1>医疗图像3D重建展示</h1>
      </el-header>
      <el-container>
        <el-aside width="350px">
          <el-card class="box-card-component">
            <div class="choice">
              <el-row>
                <el-checkbox
                  class="three_check"
                  v-model="result_staate"
                  active-value="0"
                  inactive-value="-"
                  label="三维重建功能"
                  border
                ></el-checkbox>
   
                <el-form
                  :inline="true"
                  :model="formInline"
                  class="demo-form-inline"
                >
                  <el-col :span="16">
                    <el-form-item label="">
                      <el-input
                        class="item_iso_place"
                        v-model="iso"
                        placeholder="等值面，设置为0-255"
                        label-width="50px"
                      ></el-input>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item class="item_iso_submit">
                      <el-button type="primary" @click="iso_submit"
                        >三维重建</el-button
                      >
                    </el-form-item>
                  </el-col>
                </el-form>
              </el-row>
            </div>
            <div></div>
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header"></div>
            <div
              v-if="information0.active"
              style="text-align: left; padding-left: 10px"
            >
              name:{{ information0.name }}<br />
              type:{{ information0.type }}<br />
              size:{{ information0.width }}*{{ information0.height }}
            </div>
          </el-card>
        </el-aside>
        <el-container>
          <el-main>
            <FileController
              @send_information="get_dcm_information"
              v-bind:iso="iso_change"
              v-bind:file0="dcms"
            ></FileController>
          </el-main>
          <!-- <el-footer>Footer</el-footer> -->
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>
<script>
import Controller from "@/components/Visible/Controller";
import FileController from "@/components/Visible/FileController";
import Information from "@/components/Visible/Information";
// import jquery from 'jquery';
// global.jQuery=jquery;
// import 'bootstrap/dist/css/bootstrap.min.css'

// import 'bootstrap/dist/js/bootstrap.min.js'

// import {
//   CommentDropdown,
//   PlatformDropdown,
//   SourceUrlDropdown,
// } from "./util_component/Dropdown";

const defaultForm = {
  status: "draft",
  title: "", // 文章题目
  content: "", // 文章内容
  content_short: "", // 文章摘要
  source_uri: "", // 文章外链
  image_uri: "", // 文章图片
  display_time: undefined, // 前台展示时间
  id: undefined,
  platforms: ["a-platform"],
  comment_disabled: false,
  importance: 0,
};

export default {
  name: "VisiblePage",
  components: {
    Controller,
    FileController,
    Information,
  },
  props: ["dcms"],
  data() {
    return {
      ratio: "",

      result_fusion: Number,
      postForm: Object.assign({}, defaultForm),
      result_state: Number, //0代表体渲染，1代表融合，2代表标签

      disabled: Boolean,

      informations: Array,
      information0: "",
      information1: "",
      information2: "",

      iso: "",
      iso_change: Number,


      //作为store
      // result_fusion_states: Array,
      // result_wnd_state:Number,

      // labels:Array,
      //用[-1,-1
      //   -1,-1]的形式，四个角表明四个点的状态
    };
  },
  created() {
    // this.iso = 32;
    this.iso_change = 32;
    this.dcms0 = dcms;
    this.informations = new Array(3);
    for (let i = 0; i < this.informations.length; i++) {
      this.informations[i] = {
        window: i,
        name: "",
        type: "",
        width: "",
        height: "",
        active: false,
      };
    }

    this.information0 = {
      window: 0,
      name: "",
      type: "",
      width: "",
      height: "",
      active: false,
    };
    this.information1 = {
      window: 1,
      name: "",
      type: "",
      width: "",
      height: "",
      active: false,
    };
    this.information2 = {
      window: 2,
      name: "",
      type: "",
      width: "",
      height: "",
      active: false,
    };

    this.result_state = 0;
    // this.result_wnd_state = 1 ;
    this.matting_ons = new Array([0, 0, 0]);
    this.result_fusion = 0;
    this.disabled = true;

    // this.result_fusion_states = new Array([-1,-1,-1,-1]);
    // this.labels = this.get_rand_labels(512,512);
  },
  mounted() {
    // this.matting_ons = new Array([false,false,false]);

    document
      .getElementById("dicom_files0")
      .addEventListener("change", this.handleFileSelect0);
    document
      .getElementById("dicom_files1")
      .addEventListener("change", this.handleFileSelect1);
    document
      .getElementById("dicom_files2")
      .addEventListener("change", this.handleFileSelect2);
  },

  methods: {
    get_dcm_information(data) {
      this.informations[data.window] = data;

      if (data.window == 0) {
        this.information0 = data;
      } else if (data.window == 1) {
        this.information1 = data;
      } else if (data.window == 2) {
        this.information2 = data;
      }
    },

    handleUIFileSelect0(file, file_list) {},

    handleFileSelect0(evt) {
      // console.log(1);
      evt.stopPropagation();
      evt.preventDefault();
      this.dcms0 = evt.target.files;
      // const dicom = evt.target.files[0];
      // this.imgs = new Array(this.dicoms0.length);
    },
    handleFileSelect1(evt) {
      // console.log(1);
      evt.stopPropagation();
      evt.preventDefault();
      this.dcms1 = evt.target.files;
      // const dicom = evt.target.files[0];
      // this.imgs = new Array(this.dicoms0.length);
    },
    handleFileSelect2(evt) {
      // console.log(1);
      evt.stopPropagation();
      evt.preventDefault();
      this.dcms2 = evt.target.files;
      // const dicom = evt.target.files[0];
      // this.imgs = new Array(this.dicoms0.length);
    },
    iso_submit() {
      if (this.iso == undefined || this.iso == "") this.iso = 32;

      this.iso_change = this.iso;
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
    dcms0(n_d) {
      // console.log(n_d);
    },
    result_state(new_state) {
      //   if (new_state == 0) {
      //     // this.$store.commit("visible/RESET_FUSION_STATES", [0, 1, 1, 0]);
      //     this.disabled = false;
      //   } else if (new_state == -1) {
      //     this.disabled = true;
      //   }
      if (new_state == 0) {
        this.$store.commit("visible/RESET_RESULT_VIEW_STATE", new_state);
      }
    },
    result_fusion(new_fusion, old_fusion) {
      if (new_fusion == 1) {
        // this.result_fusion_states = [0,1,1,0];//默认值
        this.$store.commit("visible/RESET_FUSION_STATES", [0, 1, 1, 0]);
        this.disabled = false;
      } else if (new_fusion == 0) {
        // this.result_fusion_states = [-1,-1,-1,-1];//默认值
        this.$store.commit("visible/RESET_FUSION_STATES", [-1, -1, -1, -1]);
        this.disabled = true;
      }
    },
  },
};
</script>


<style lang="scss" scoped>
@import "~@/styles/mixin.scss";

.createPost-container {
  position: relative;

  .createPost-main-container {
    padding: 40px 45px 20px 50px;

    .postInfo-container {
      position: relative;
      @include clearfix;
      margin-bottom: 10px;

      .postInfo-container-item {
        float: left;
      }
    }
  }

  .word-counter {
    width: 40px;
    position: absolute;
    right: 10px;
    top: 0px;
  }
}

.article-textarea ::v-deep {
  textarea {
    padding-right: 40px;
    resize: none;
    border: none;
    border-radius: 0px;
    border-bottom: 1px solid #bfcbd9;
  }
}

// .choice {
//   background: rgb(214, 214, 214);
//   color: #fff;
//   padding: 10px;
//   z-index: -1;
// }
.three_check {
  background: rgb(255, 255, 255);
}
.el-header,
.el-footer {
  background-color: #b3c0d1;
  color: #333;
  text-align: center;
  line-height: 60px;
}

.el-aside {
  // width: 350px;
  background-color: #eaf1f8;
  color: #333;
  text-align: center;
  line-height: 40px;
}

.el-main {
  background-color: #e9eef3;
  color: #333;
  text-align: center;
}

body > .el-container {
  margin-bottom: 40px;
}

.el-container:nth-child(5) .el-aside,
.el-container:nth-child(6) .el-aside {
  line-height: 260px;
}

.el-container:nth-child(7) .el-aside {
  line-height: 320px;
}
.file_input {
  border: 1.5px solid rgb(255, 255, 255);
  border-radius: 10px;
}
.box-card .el-card__header {
  padding: 0px;
  background: #b3c0d1;
}
.el-row {
  margin-bottom: 10px;
}
// .item_iso_place{
//   width: 50%;
// }
// .item_iso_submit{
//   width: 25%
// }
</style>
<style lang="css">
</style>