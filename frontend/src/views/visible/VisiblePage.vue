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
              <el-dropdown :show-timeout="100" trigger="click">
                <el-button plain>
                  <!-- {{ !comment_disabled ? "Comment: opened" : "Comment: closed" }} -->
                  <span v-if="result_state == 0">体渲染</span>
                  <span v-else-if="result_state == 1">影像融合</span>
                  <span v-else-if="result_state == 2">标签标记</span>
                  <i class="el-icon-caret-bottom el-icon--right" />
                </el-button>
                <el-dropdown-menu slot="dropdown" class="no-padding">
                  <el-dropdown-item>
                    <el-radio-group
                      v-model="result_state"
                      style="padding: 10px"
                    >
                      <el-radio :label="0"> 体渲染 </el-radio>
                      <el-radio :label="1"> 影像融合 </el-radio>
                      <el-radio :label="2"> 标签标记 </el-radio>
                    </el-radio-group>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
              <el-checkbox
                class="fusion_check"
                v-model="result_fusion"
                active-value="1"
                inactive-value="0"
                label="图像融合功能"
                border
                :disabled="disabled"
              ></el-checkbox>
              </el-row>
              
              <el-row>
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
                  <el-button type="primary" @click="iso_submit">三维重建</el-button>
                </el-form-item>
                </el-col>

              </el-form>
              </el-row>

            </div>
            <div>
              
            </div>
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header">窗口0</div>
            <div
              v-if="information0.active"
              style="text-align: left; padding-left: 10px"
            >
              name:{{ information0.name }}<br />
              type:{{ information0.type }}<br />
              size:{{ information0.width }}*{{ information0.height }}
            </div>
            <input
              type="file"
              id="dicom_files0"
              multiple="multiplt"
              placeholder="本地dicom文件上传"
            />
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header">窗口1</div>
            <div
              v-if="information1.active"
              style="text-align: left; padding-left: 10px"
            >
              name:{{ information1.name }}<br />
              type:{{ information1.type }}<br />
              size:{{ information1.width }}*{{ information0.height }}
            </div>
            <input
              type="file"
              id="dicom_files1"
              multiple="multiplt"
              placeholder="本地dicom文件上传"
            />
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header">窗口2</div>
            <div
              v-if="information2.active"
              style="text-align: left; padding-left: 10px"
            >
              name:{{ information2.name }}<br />
              type:{{ information2.type }}<br />
              size:{{ information2.width }}*{{ information0.height }}
            </div>
            <input
              type="file"
              id="dicom_files2"
              multiple="multiplt"
              placeholder="本地dicom文件上传"
            />
          </el-card>
        </el-aside>
        <el-container>
          <el-main>
            <FileController
              @send_information="get_dcm_information"
              v-bind:iso="iso_change"
              v-bind:file0="dcms0"
              v-bind:file1="dcms1"
              v-bind:file2="dcms2"
              v-bind:result_fusion="result_fusion"
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
  data() {
    return {
      dcms0: "",
      dcms1: "",
      dcms2: "",
      ratio: "",

      result_fusion: Number,
      postForm: Object.assign({}, defaultForm),
      result_state: Number, //0代表体渲染，1代表融合，2代表标签

      disabled: Boolean,

      informations: Array,
      information0: "",
      information1: "",
      information2: "",

      iso:'',
      iso_change:Number,

      //作为store
      // result_fusion_states: Array,
      // result_wnd_state:Number,

      // labels:Array,
      //用[-1,-1
      //   -1,-1]的形式，四个角表明四个点的状态
    };
  },
  created() {
    this.iso_change = 32;
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
    iso_submit(){
      if (this.iso == undefined || this.iso == '') this.iso = 32;
      this.iso_change = this.iso;

      // if(this.iso==undefined)this.iso=32;
      // this.iso_change = this.iso;

    }
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
      if (new_state == 1) {
        // this.$store.commit("visible/RESET_FUSION_STATES", [0, 1, 1, 0]);
        this.disabled = false;
      } else if (new_state == 0) {
        this.disabled = true;
      }
      this.$store.commit("visible/RESET_RESULT_VIEW_STATE", new_state);
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
.fusion_check {
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