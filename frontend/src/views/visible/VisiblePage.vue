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
                    <span v-if="result_state == 0">三维重建</span>
                    <span v-else-if="result_state == 1">影像融合</span>
                    <!-- <span v-else-if="result_state == 2">标签标记</span> -->
                    <span v-else-if="result_state == 3">三维显示</span>

                    <i class="el-icon-caret-bottom el-icon--right" />
                  </el-button>
                  <el-dropdown-menu slot="dropdown" class="no-padding">
                    <el-dropdown-item>
                      <el-radio-group
                        v-model="result_state"
                        style="padding: 10px"
                      >
                        <el-radio :label="0"> 三维重建 </el-radio>
                        <el-radio :label="1"> 影像融合 </el-radio>
                        <!-- <el-radio :label="2"> 标签标记 </el-radio> -->
                        <el-radio :label="3"> 三维显示 </el-radio>
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

              <el-row v-if="this.result_state == 0">
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
                        placeholder="等值面设置为0-255"
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

              <el-row v-if="this.result_state == 1 && result_fusion == 1">
                <div>
                  <el-col :span="16">
                    <span class="fusion_text">结果窗口0对应切片</span>
                  </el-col>
                  <el-col :span="8">
                    <el-input
                      v-model="result_fusion_states[0]"
                      placeholder="结果窗口0对应切片"
                      label-width="50px"
                    ></el-input>
                  </el-col>
                </div>

                <div>
                  <el-col :span="16">
                    <span class="fusion_text">结果窗口1对应切片</span>
                  </el-col>
                  <el-col :span="8">
                    <el-input
                      v-model="result_fusion_states[1]"
                      placeholder="结果窗口1对应切片"
                      label-width="50px"
                    ></el-input>
                  </el-col>
                </div>

                <div>
                  <el-col :span="16">
                    <span class="fusion_text">结果窗口2对应切片</span>
                  </el-col>
                  <el-col :span="8">
                    <el-input
                      v-model="result_fusion_states[2]"
                      placeholder="结果窗口2对应切片"
                      label-width="50px"
                    ></el-input>
                  </el-col>
                </div>

                <div>
                  <el-col :span="16">
                    <span class="fusion_text">结果窗口3对应切片</span>
                  </el-col>
                  <el-col :span="8">
                    <el-input
                      v-model="result_fusion_states[3]"
                      placeholder="结果窗口3对应切片"
                      label-width="50px"
                    ></el-input>
                  </el-col>
                </div>
              </el-row>

              <el-row v-if="this.result_state == 3">
                <div>
                  <span class="visible_text">切片0可见性</span>
                  <el-switch
                    v-model="visible_states[0]"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    active-value="true"
                    inactive-value="false"
                  >
                  </el-switch>
                </div>

                <div>
                  <span class="visible_text">切片1可见性</span>
                  <el-switch
                    v-model="visible_states[1]"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    active-value="true"
                    inactive-value="false"
                  >
                  </el-switch>
                </div>

                <div>
                  <span class="visible_text">切片2可见性</span>
                  <el-switch
                    v-model="visible_states[2]"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    active-value="true"
                    inactive-value="false"
                  >
                  </el-switch>
                </div>
              </el-row>
              <el-row>
                  <!-- <el-button type="danger" round>重置</el-button> -->

              </el-row>
            </div>
            <div></div>
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header">窗口0</div>
            <div id="query0">
              <el-select
                v-model="data_id0"
                filterable
                placeholder="请选择数据集"
              >
                <el-option
                  v-for="item in data_list"
                  :key="item.title"
                  :label="item.title"
                  :value="item.id"
                >
                </el-option>
              </el-select>
            </div>
            <!-- <div id="label0">            
              <input
              type="file"
              id="marks_file_input0"
              placeholder="标签选择"
              />
            </div> -->

            <div
              v-if="information0.active"
              style="text-align: left; padding-left: 10px"
            >
              name:{{ information0.name }}<br />
              type:{{ information0.type }}<br />
              size:{{ information0.width }}*{{ information0.height }}
            </div>
            <div>
              <!-- <span>本地文件：</span> -->
              <input
              type="file"
              id="dicom_files0"
              multiple="multiplt"
              placeholder="本地dicom文件上传"
            />
            </div>
            <!-- <input
              type="file"
              id="dicom_files0"
              multiple="multiplt"
              placeholder="本地dicom文件上传"
            /> -->
          </el-card>

          <el-card class="box-card" style="margin-top: 10px">
            <div slot="header">窗口1</div>
            <div id="query0">
              <el-select
                v-model="data_id1"
                filterable
                placeholder="请选择数据集"
              >
                <el-option
                  v-for="item in data_list"
                  :key="item.title"
                  :label="item.title"
                  :value="item.id"
                >
                </el-option>
              </el-select>
            </div>
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
            <el-select v-model="data_id2" filterable placeholder="请选择数据集">
              <el-option
                v-for="item in data_list"
                :key="item.title"
                :label="item.title"
                :value="item.id"
              >
              </el-option>
            </el-select>
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
              v-bind:marks_file0="marks_file0"
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

import {
  fetchList,
  fetchPv,
  createDataset,
  updateDataset,
  deleteDataset,
} from "@/api/dataset";

// import jquery from 'jquery';
// global.jQuery=jquery;
// import 'bootstrap/dist/css/bootstrap.min.css'

// import 'bootstrap/dist/js/bootstrap.min.js'

// import {
//   CommentDropdown,
//   PlatformDropdown,
//   SourceUrlDropdown,
// } from "./util_component/Dropdown";

// const defaultForm = {
//   status: "draft",
//   title: "", // 文章题目
//   content: "", // 文章内容
//   content_short: "", // 文章摘要
//   source_uri: "", // 文章外链
//   image_uri: "", // 文章图片
//   display_time: undefined, // 前台展示时间
//   id: undefined,
//   platforms: ["a-platform"],
//   comment_disabled: false,
//   importance: 0,
// };

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

      marks_file0:"",
      marks_file1:"",
      marks_file2:"",

      result_fusion: Number,
      // postForm: Object.assign({}, defaultForm),
      result_state: Number, //0代表体渲染，1代表融合，2代表标签

      disabled: Boolean,

      informations: Array,
      information0: "",
      information1: "",
      information2: "",

      iso: "",
      iso_change: Number,

      visible_states: Array,

      //查询数据集部分
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        importance: undefined,
        title: undefined,
        type: undefined,
        sort: "+id",
        sources: [],
        body: [],
        format: [],
        model: [],
      },

      data_list: Array,
      total_data_list: Array,
      data_id0: "",
      data_id1: "",
      data_id2: "",

      //作为store
      result_fusion_states: Array,
      // result_wnd_state:Number,

      // labels:Array,
      //用[-1,-1
      //   -1,-1]的形式，四个角表明四个点的状态
    };
  },
  created() {
    this.result_fusion_states = [0, 1, 1, 0];
    this.visible_states = new Array([true, true, true]);
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

    this.get_list();
  },
  mounted() {
    // this.matting_ons = new Array([false,false,false]);
    // document
    //   .getElementById("marks_file_input0")
    //   .addEventListener("change", this.handleLabelSelect0);

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
    get_list() {
      this.listLoading = true;
      fetchList(this.listQuery).then((response) => {
        this.data_list = response.data.items;
        this.total_data_list = response.data.total;
        // this.sourcesOptions = response.data.option.sourceOptions
        // this.bodyOptions = response.data.option.bodyOptions
        // this.formatOptions = response.data.option.formatOptions
        this.listLoading = false;
      });
    },
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
    handleLabelSelect0(evt){
      evt.stopPropagation();
      evt.preventDefault();
      this.marks_file0 = evt.target.files[0];
    },

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

      // if(this.iso==undefined)this.iso=32;
      // this.iso_change = this.iso;
    },
    query_data(id) {
      return "";
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
      // console.log(this.result_fusion);
      if (new_fusion == 1) {
        // this.result_fusion_states = [0,1,1,0];//默认值
        this.$store.commit("visible/RESET_FUSION_STATES", [0, 1, 1, 0]);
        // this.disabled = false;
      } else if (new_fusion == 0) {
        // this.result_fusion_states = [-1,-1,-1,-1];//默认值
        this.$store.commit("visible/RESET_FUSION_STATES", [-1, -1, -1, -1]);
        // this.disabled = true;
      }
    },

    result_fusion_states(new_states) {
      if (this.result_fusion == 1) {
        this.$store.commit("visible/RESET_FUSION_STATES", new_states);
      }
    },

    visible_states(new_states) {
      // console.log(new_states)
      this.$store.commit("visible/RESET_VISIBLE_STATES", new_states);
      // console.log(this.$store.getters.visible_states);
    },

    listLoading(new_l) {
      if (new_l == false) {
        // console.log(this.data_list,this.total_data_list)
      }
    },

    data_id0(new_id) {
      file0 = this.query_data(new_id);
    },
    data_id1(new_id) {
      file1 = this.query_data(new_id);
    },
    data_id2(new_id) {
      file2 = this.query_data(new_id);
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