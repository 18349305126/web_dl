<template>
  <div id="fileController">
    <div id="controller">
      <Controller
        v-bind:raws="raws"
        v-bind:raw_change="change"
        v-bind:normals="normals"
        v-bind:vers="vers"
        v-bind:marks="marks"
        v-bind:loading_vers_normals="loading_vers_normals"
      >
      </Controller>
    </div>
  </div>
</template>

<script>
// //引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import VisibleWindow from "./window/VisibleWindow";
import ResultWindow from "./window/ResultWindow";
import Controller from "./Controller";
import { volRender } from "@/api/visible";
import { volRender2 } from "@/api/visible";

import { testRender } from "@/api/visible";
// import { test } from "@/api/project";

import axios from "axios";
//axios.defaults.baseURL = process.env.VUE_APP_BASE_API; //关键代码
axios.defaults.baseURL = "http://localhost:8080"; //关键代码
// import { dot } from "mathlab";
// import { min, Tensor } from "@tensorflow/tfjs";

import * as cornerstone from "cornerstone-core";
import * as dicomParser from "dicom-parser";
// import * as math from "mathjs";

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
import * as cornerstoneWADOImageLoader from "../../../public/static/dist/cornerstoneWADOImageLoader.js";
// var c = require("../../../static/opencvjs/opencv_js.js");
// import cv from "../../../static/opencvjs/opencv_js.js";

// Cornerstone 工具外部依赖
import Hammer from "hammerjs";
import * as cornerstoneMath from "cornerstone-math";
import * as cornerstoneTools from "cornerstone-tools";
// import { RawShaderMaterial } from "node_modules/three/build/three";

// import DicomResultWindow from './dicomhandle/DicomResultWindow.vue';

// Specify external dependencies
cornerstoneTools.external.Hammer = Hammer;
cornerstoneTools.external.cornerstone = cornerstone;
cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath;

//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

cornerstone.registerImageLoader("http", cornerstoneWADOImageLoader.loadImage);
cornerstone.registerImageLoader("https", cornerstoneWADOImageLoader.loadImage);

//配置 webWorker (必须配置)
//注意这里的路径问题  如果路径不对 cornerstoneWADOImageLoaderWebWorker 会报错 index.html Uncaught SyntaxError: Unexpected token <
var config = {
  webWorkerPath: "static/dist/cornerstoneWADOImageLoaderWebWorker.js",
  taskConfiguration: {
    decodeTask: {
      codecsPath: "static/dist/cornerstoneWADOImageLoaderCodecs.js",
    },
  },
};

if (!cornerstoneWADOImageLoader.webWorkerManager.config) {
  // console.log(cornerstoneWADOImageLoader.webWorkerManager.config);
  cornerstoneWADOImageLoader.webWorkerManager.initialize(config);
}

export default {
  name: "FileController",
  components: { VisibleWindow, ResultWindow, Controller },
  props: ["file0", "file1", "file2", "out_raws","iso","marks_file0"],
  data() {
    return {
      //窗口参数的设置
      // wnd_w: "256px",
      // wnd_h: "256px",
      active_state: {
        fi0: Boolean,
        fi1: Boolean,
        fi2: Boolean,
      },

      wnd_w: 350,
      wnd_h: 350,

      //dicom文件的数据
      // file0: "", //存储所有dicom文件
      // file0_num: Number,
      // file1_num: Number,
      dicoms_nums: Array,
      // file0:"",=

      dicom_wids: Array,
      dicom_heis: Array,
      result_mat_width: Array,
      result_mat_height: Array,

      // dicom: "", //当下展示的dicom文件
      imgs: Array,

      // raws[0]: "", //三维数据场
      raws: Array,
      read_nums: Array,
      marks: Array,
      //体渲染的坐标与法向量
      vers: Array,
      normals: Array,
      loading_vers_normals: false, //是否在加载数据
      finished0: Boolean, //判断图像是否加载完成
      finished1: Boolean, //判断图像是否加载完成
      finished2: Boolean, //判断图像是否加载完成

      change: Boolean, //由于无法监控数组，所以用这个来向controller传递raw改变的信息

      tot_marks: Array,
      x_render_scale:Number,
      y_render_scale:Number,
      z_render_scale:Number,

      marks0:Array

      // x_pix_spacing:Number,
      // y_pix_spacing:Number,
      // z_pix_spacing:Number,

      // back_test: Number,
      // result_wnd_state:Number,

      // finishes: Array,
    };
  },
  created() {
    // this.x_len = 0;
    // this.y_len = 0;


    this.back_test = 0;
    this.dicoms_nums = new Array([0, 0, 0]);
    this.read_nums = new Array([0, 0, 0]);
    this.dicom_wids = new Array([0, 0, 0]);
    this.dicom_heis = new Array([0, 0, 0]);
    this.raws = new Array(3);
    this.imgs = new Array(3);
    this.change = false;

    // this.pix_row_spacings = new Array([this.x_pix_spacing,this.y_pix_spacing,this.x_pix_spacing]);

    // this.finishes = new Array(false,false,false);

    this.active_state.fi0 = false;
    this.active_state.fi1 = false;
    this.active_state.fi2 = false;

    this.finished0 = false;
    this.finished1 = false;
    this.finished2 = false;

    this.x_render_scale = 0.2;
    this.y_render_scale = 0.2;
    this.z_render_scale = 0.5;
  },
  mounted() {
    // console.log(cornerstoneWADOImageLoader);
    this.tot_marks = this.get_rand_tot_marks(512, 512);
    this.marks = this.tot_marks;
  },
  methods: {
    getImg(imageId) {
      const _this = this;
      // let img;
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          _this.img = image;
        },
        function (err) {
          alert(err);
        }
      );
    },
    appendImg(dcm, z_idx, idx) {
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dcm);
      const _this = this;
      // console.log(this.read_num);
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          // console.log(image);
          // console.log(images.getPixelData());

          _this.imgs[idx][z_idx] = image;
          _this.read_nums[idx]++;

          if (_this.read_nums[idx] == _this.dicoms_nums[idx]) {
            if (idx == 0) {
              // console.log(1);
              _this.finished0 = true;
            } else if (idx == 1) {
              _this.finished1 = true;
            } else if (idx == 2) {
              _this.finished2 = true;
            }
            console.log("加载完成", idx);
          }
          // console.log(_this.imgs[0]);
        },
        function (err) {
          alert(err);
        }
      );
    },

    StringFormat() {
      if (arguments.length == 0) return null;
      var str = arguments[0];
      for (var i = 1; i < arguments.length; i++) {
        var re = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        str = str.replace(re, arguments[i]);
      }
      return str;
    },
    getStyle() {
      let style = this.StringFormat(
        "width: {0}px;height: {1}px;position: relative;color: white;display: inline-block;border-style: solid;border-color: black;",
        this.wnd_w + 20,
        this.wnd_h + 20
      );

      // console.log(style);
      return style;
    },
    getStyle2() {
      let style = this.StringFormat(
        "width: {0}px;height: {1}px;position: relative;color: white;",
        this.wnd_w + 20,
        this.wnd_h + 20
      );

      // console.log(style);
      return style;
    },
    judgeEmpty(array) {
      let len = array.length;
      for (let i = 0; i < len; i++) {
        if (array[i] == undefined) {
          return false;
        }
      }
      return true;
    },

    array2mat(arr, row, col) {
      let len = arr.length;
      if (len != row * col) {
        throw new Error(
          this.StringFormat(
            "数组与矩阵必须匹配，当前数组长度{0}，而要求的矩阵宽度{1}，矩阵长度{2}",
            len,
            row,
            col
          )
        );
      }

      let mat = new Array(row);
      for (var i = 0; i < row; i++) {
        mat[i] = new Uint16Array(col);
      }

      for (let i = 0; i < row; i++) {
        for (let j = 0; j < col; j++) {
          mat[i][j] = arr[i * row + j];
        }
      }
      return mat;
    },

    rebuild3D(images, x, y, z) {
      // console.log(images[0].getPixelData().length);
      let raws = new Array(x);
      for (let i = 0; i < x; i++) {
        raws[i] = new Array(y);
        for (let j = 0; j < y; j++) {
          raws[i][j] = new Uint16Array(z); //暂时使用unit16作为...
        }
      }
      let max = -1;

      for (let i = 0; i < z; i++) {
        let mat;
        try {
          mat = this.array2mat(Array.from(images[i].getPixelData()), x, y);
        } catch (e) {
          console.log(e);
        }
        for (let j = 0; j < x; j++) {
          for (let k = 0; k < y; k++) {
            if (max < mat[j][k]) max = mat[j][k];

            raws[j][k][i] = mat[j][k];
          }
        }
      }
      for (let i = 0; i < x; i++) {
        for (let j = 0; j < y; j++) {
          for (let k = 0; k < z; k++) {
            raws[i][j][k] = (raws[i][j][k] / max) * 256;
          }
        }
      }
      // this.raws[0] = raws;
      return raws;
      // console.log("3D重建大小：",sizeof(raws[0]));
      // console.log("原来数据大小：",sizeof(this.imgs[0]));
    },
    resize_r(raw, x_alp, y_alp) {
      let x_len = raw.length;
      let y_len = raw[0].length;
      let z_len = raw[0][0].length;

      let resize_x_len = Math.round(x_len * x_alp);
      let c = Math.round(y_len * y_alp);

      let resize_raw = new Array(resize_x_len);
      for (let i = 0; i < resize_x_len; i++) {
        resize_raw[i] = new Array(resize_x_len);
        for (let j = 0; j < resize_x_len; j++) {
          resize_raw[i][j] = new Uint16Array(z_len);
          for (let k = 0; k < z_len; k++) {
            let x = i / x_alp;
            let y = j / y_alp;
            let x0 = Math.floor(x);
            let y0 = Math.floor(y);
            let x1 = Math.ceil(x);
            let y1 = Math.ceil(y);
            let det = (y1 - y0) * (x1 - x0);

            if (x0 == x1 || y0 == y1) resize_raw[i][j][k] = raw[x0][y0][k];
            else {
              resize_raw[i][j][k] =
                0.25 * raw[x0][y0][k] +
                0.25 * raw[x1][y0][k] +
                0.25 * raw[x0][y1][k] +
                0.25 * raw[x1][y1][k];
            }
            // resize_raw[i][j][k] =
            //   (((y1 - y) * (x1 - x)) / det) * raw[x0][y0][k] +
            //   (((y1 - y) * (x - x0)) / det) * raw[x1][y0][k] +
            //   (((y - y0) * (x1 - x)) / det) * raw[x0][y1][k] +
            //   (((y - y0) * (x - x0)) / det) * raw[x1][y1][k];
          }
        }
      }
      return resize_raw;
    },

    resize_r_total(raw, x_alp, y_alp, z_alp) {
      let x_len = raw.length;
      let y_len = raw[0].length;
      let z_len = raw[0][0].length;

      let resize_x_len = Math.round(x_len * x_alp);
      let resize_y_len = Math.round(y_len * y_alp);
      let resize_z_len = Math.round(z_len * z_alp);

      let resize_raw = new Array(resize_x_len);
      for (let i = 0; i < resize_x_len; i++) {
        resize_raw[i] = new Array(resize_y_len);
        for (let j = 0; j < resize_y_len; j++) {
          resize_raw[i][j] = new Uint16Array(resize_z_len);
          for (let k = 0; k < z_len; k++) {
            let x = i / x_alp;
            let y = j / y_alp;
            let z = k / z_alp;
            let x0 = Math.floor(x);
            let y0 = Math.floor(y);
            let z0 = Math.floor(z);
            let x1 = Math.ceil(x);
            let y1 = Math.ceil(y);
            let z1 = Math.ceil(z);

            if (x0 == x1 || y0 == y1 || z0==z1) resize_raw[i][j][k] = raw[x0][y0][z0];
            else {
              resize_raw[i][j][k] = (raw[x0][y0][z0] + raw[x1][y0][z0] + raw[x0][y1][z0] + raw[x1][y1][z0] +
              raw[x0][y0][z1] + raw[x1][y0][z1] + raw[x0][y1][z1] + raw[x1][y1][z1])*0.125;
   
            }
            // resize_raw[i][j][k] =
            //   (((y1 - y) * (x1 - x)) / det) * raw[x0][y0][k] +
            //   (((y1 - y) * (x - x0)) / det) * raw[x1][y0][k] +
            //   (((y - y0) * (x1 - x)) / det) * raw[x0][y1][k] +
            //   (((y - y0) * (x - x0)) / det) * raw[x1][y1][k];
          }
        }
      }
      return resize_raw;
    },

    process_dcms(dcms, idx) {
      this.imgs[idx] = new Array(dcms.length);

      this.dicoms_nums[idx] = dcms.length;
      // this.z_len = this.dicoms_nums[idx];
      this.read_nums[idx] = 0;
      // if(idx==1)console.log("before",this.read_num);
      // console.log(idx,this.dicoms_nums[idx]);
      for (let i = 0; i < this.dicoms_nums[idx]; i++) {
        this.appendImg(dcms[i], i, idx);
      }
    },

    get_raw(imgs) {
      //工具函数
      let x_len = imgs[0].width;
      let y_len = imgs[0].height;
      let z_len = imgs.length;

      let raw = this.rebuild3D(imgs, x_len, y_len, z_len);
      return raw;
    },

    judge_file_type(file) {
      //工具函数
      //-1代表无效，0代表dcm，1代表nii,2代表mha
      let f_name;

      if (Object.prototype.toString.call(file) === "[object FileList]") {
        f_name = file[0].name;
      } else if (Object.prototype.toString.call(file) === "[object File]") {
        f_name = file.name;
      } else {
        return -1;
      }
      let idx = f_name.lastIndexOf(".");
      let file_type = f_name.substr(idx + 1).toLocaleLowerCase();
      if (file_type == "dcm" || file_type == "dicom") {
        return 0;
      } else if (file_type == "nii") {
        return 1;
      } else if (file_type == "mha") {
        return 2;
      } else {
        return -1;
      }
    },

    get_file_name(file) {
      let f_name;
      if (Object.prototype.toString.call(file) === "[object FileList]") {
        f_name = file[0].name;
        // let common_file_name = this.get_common_str(file[0].name,file[file.length-1].name);
        // let common_file_name = file[0].name
        // return  common_file_name;

        let idx = f_name.lastIndexOf(".");
        let file_name = f_name.substr(0, idx);
        return file_name;
      } else if (Object.prototype.toString.call(file) === "[object File]") {
        f_name = file.name;
        let idx = f_name.lastIndexOf(".");
        let file_name = f_name.substr(0, idx);
        return file_name;
      } else {
        return null;
      }
    },

    get_common_str(str1, str2) {
      let len;
      if (str1.length < str2.length) len = str1.length;
      else len = str2.length;
      let idx = len;

      for (let i = 0; i < len; i++) {
        if (str1[i] != str2[i]) {
          if (str1[i] == "-" || str1[i] == ".") {
            idx = i - 1;
          }
          idx = i;
          break;
        }
      }
      // console.log(idx)
      return str1.substr(0, idx);
    },

    get_vers_norms(raw) {
      //测试数据
      //   this.read_vers_norms(
      //     "static/model/test/json_test.json",
      //     "static/model/test/normal_test.json"
      //   );
    },
    read_vers_norms(data_url, normal_url) {
      // this.loading_vers_normals = true;
      this.read_vers(data_url);
      this.read_normals(normal_url);
    },

    read_vers(url) {
      let formData = new FormData();
      formData.append("x",1);
      axios({
        url: url,
        method: "post",
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }).then((response) => {
        console.log(response);
        if (response.data == "Not Found" || response.data == "") {
          const that = this;
          setTimeout(function () {
            that.read_vers(url);
          }, 2000);
        } else {
          this.vers = new Float32Array(response.data);
          if (this.vers.length > 0 && this.normals.length > 0) {
            this.loading_vers_normals = false;
          }
          //console.log(this.vers)
        }
      });
    },
    read_normals(url) {
        let formData = new FormData();
      formData.append("x",1);
      axios({
        url: url,
        method: "post",
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }).then((response) => {
        console.log(response);
        if (response.data == "Not Found" || response.data == "") {
          const that = this;
          setTimeout(function () {
            that.read_normals(url);
          }, 2000);
        } else {
          this.normals = new Float32Array(response.data);
          if (this.vers.length > 0 && this.normals.length > 0) {
            this.loading_vers_normals = false;
          }
          //console.log(this.normals)
        }
      });
    },

    get_rand_tot_marks(wid, hei) {
      //工具函数
      let w_n = 4;
      let h_n = 4;
      let marks = new Array(wid);
      for (let i = 0; i < wid; i++) {
        marks[i] = new Array(hei);
        for (let j = 0; j < hei; j++) {
          marks[i][j] = 0;
        }
      }
      // let label = Math.round(Math.random() * 10);
      for (let w_i = 0; w_i < w_n - 1; w_i++) {
        for (let h_j = 0; h_j < h_n - 1; h_j++) {
          let label = Math.round(Math.random() * 10);
          label =
            ((((w_i + 3) * label * 941) % 569) +
              (((h_j + 3) * label * 919) % 1013)) %
            10; //随机生成的

          for (let i = (wid / w_n) * w_i; i < (wid / w_n) * (w_i + 1); i++) {
            for (let j = (hei / h_n) * h_j; j < (hei / h_n) * (h_j + 1); j++) {
              marks[i][j] = label;
            }
          }
        }
      }
      return marks;
    },

    init_mark(wid, hei) {
      //将mark全部置为-1
      let marks = new Array(wid);
      for (let i = 0; i < wid; i++) {
        marks[i] = new Array(hei);
        for (let j = 0; j < hei; j++) {
          marks[i][j] = 0;
        }
      }
      return marks;
    },

    add_mark(marks, tot_marks, idxs) {
      let row = marks.length;
      let col = marks[0].length;

      for (let i = 0; i < row; i++) {
        for (let j = 0; j < col; j++) {
          if (tot_marks[i][j] in idxs) {
            marks[i][j] = tot_marks[i][j];
          }
        }
      }
      return marks;
    },

    message(wnd_id) {
      let name;
      let type_num;
      let type;
      if (wnd_id == 0) {
        type_num = this.judge_file_type(this.file0);
        name = this.get_file_name(this.file0);
      } else if (wnd_id == 1) {
        type_num = this.judge_file_type(this.file1);
        name = this.get_file_name(this.file1);
      } else if (wnd_id == 2) {
        type_num = this.judge_file_type(this.file2);
        name = this.get_file_name(this.file2);
      }

      if (type_num == 0) {
        type = "dcm";
      } else if (type_num == 1) {
        type = "nii";
      } else if (type_num == 2) {
        type = "mha";
      }

      let mess = {
        window: wnd_id,
        name: name,
        type: type,
        width: this.imgs[wnd_id][0].width,
        height: this.imgs[wnd_id][0].height,
        active: true,
      };

      this.$emit("send_information", mess);
    },

    clear(wnd_id) {
      this.raws[wnd_id] = null;
      this.change = !this.change;
      this.imgs[wnd_id] = null;
      // this.file0.destroy();
      if (wnd_id == 0) {
        this.file0 = null;
        // this.imgs[wnd_id].destroy();
        this.finished0 = false;
      } else if (wnd_id == 1) {
        this.file1 = null;
        // this.imgs[wnd_id].destroy();
        this.finished1 = false;
      } else if (wnd_id == 2) {
        this.file2 = null;
        // this.imgs[wnd_id].destroy();
        this.finished2 = false;
      }
    },

    post_raw(raw, wnd_id, x_scale, y_scale, z_scale,iso) {
      // raw = this.resize_r(raw, x_scale, y_scale);
      raw = this.resize_r_total(raw, x_scale, y_scale,z_scale);
      let formData = new FormData();
      let x_len = raw.length;
      let y_len = raw[0].length;
      let z_len = raw[0][0].length;

      let file = new File(
        [JSON.stringify(raw)],
        this.StringFormat("raw{0}", wnd_id)
      );
      // let file = new File( raw, this.StringFormat("raw{0}", wnd_id));

      // let file = this.file0[0];
      // console.log(file);

      formData.append("file", file);
      // formData.append("x_len",x_len);

      this.loading_vers_normals = true;
      this.vers = Array();
      this.normals = Array();

      axios({
        url: "/visible/render?isolevel=" + iso,
        method: "post",
        data: formData,
        //  headers: {
        //   'Content-Type': 'application/x-www-form-urlencoded'
        //  },
        // headers: {
        //   "Content-Type": "application/json",
        // },
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
        .then((res) => {
          console.log(res);
          this.read_vers_norms(res.data.versUrl, res.data.normsUrl);
        })
        .catch((err) => {
          this.loading_vers_normals = false;

          console.log(err);
        });
    },

    post_list(raw) {
      let req = { list: raw };
      req = JSON.stringify(req);
      console.log(req);
      axios({
        url: "/visible/render2",
        method: "post",
        data: req,
      }).then((response) => {
        console.log(response);
      });

      // formData.append("file", file);
      // axios({
      //   url: "/visible/render",
      //   method: "post",
      //   data: formData,
      //   //  headers: {
      //   //   'Content-Type': 'application/x-www-form-urlencoded'
      //   //  },
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      // })
      //   .then((res) => {
      //     console.log(res);
      //   })
      //   .catch((err) => {
      //     console.log(err);
      //   });
    },
    // test() {
    //   let a = 10;
    //   testRender(a).then(
    //     (response) => {
    //       console.log(response.data);
    //     },
    //     (response) => {
    //       console.log("error");
    //     }
    //   );
    // },
  },

  watch: {
    // back_test(new_b){
    //   console.log(new_b);
    // },

    file0(new_file0, old_dcms0) {
      if (new_file0 != undefined) {
        this.active_state.fi0 = true;
        let file_type = this.judge_file_type(new_file0);
        if (file_type == 0) {
          //0代表dcm
          if (this.finished0 == true) {
            // this.clear(0)
          }
          this.process_dcms(new_file0, 0);
          // test().then(
          //   (response) => {
          //     console.log(response);
          //   },
          //   (response) => {
          //     console.log("err");
          //   }
          // );

          // this.post_list([1,1]);
          // this.post_raw(this.raws[0], 0, 0.25, 0.25, 32);
          this.post_raw(this.raws[0], 0, this.x_render_scale, this.y_render_scale, this.z_render_scale, 32);

        }
      }
    },
    file1(new_file1, old_dcms1) {
      if (new_file1 != undefined) {
        this.active_state.fi1 = true;
        let file_type = this.judge_file_type(new_file1);
        if (file_type == 0) {
          //0代表dcm
          if (this.finished1 == true) {
            // this.clear(1)
          }

          this.process_dcms(new_file1, 1);
        }
      }
    },
    file2(new_file2, old_dcms2) {
      if (new_file2 != undefined) {
        this.active_state.fi2 = true;
        let file_type = this.judge_file_type(new_file2);
        if (file_type == 0) {
          //0代表dcm
          if (this.finished2 == true) {
            // this.clear(2)
          }
          this.process_dcms(new_file2, 2);
        }
      }
    },

    marks_file0(new_mark){
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(new_mark);
      const _this = this;
      // console.log(this.read_num);
      cornerstone.loadAndCacheImage(imageId).then(
        function (image) {
          console.log(image);
          console.log(image.getPixelData());
        },
        function (err) {
          alert(err);
        }
      );

    },
    finished0(new_f, old_f) {
      if (new_f) {
        let wnd_id = 0;
        this.raws[wnd_id] = this.get_raw(this.imgs[wnd_id]);
        this.change = !this.change;

        this.message(wnd_id);
        // this.file0.destroy();
        this.file0 = null;
        // this.imgs[wnd_id].destroy();
        this.imgs[wnd_id] = null;

        this.get_vers_norms(this.raws[wnd_id]);
        // setTimeout(() => {
        //   this.finished0 = false;
        // }, 2000);

        // this.finished0 = false;
        // this.post_list(this.raws[0]);
      }
    },
    finished1(new_f, old_f) {
      if (new_f) {
        let wnd_id = 1;
        this.raws[wnd_id] = this.get_raw(this.imgs[wnd_id]);
        this.change = !this.change;

        this.message(wnd_id);

        // this.file0.destroy();
        this.file1 = null;
        // this.imgs[wnd_id].destroy();
        this.imgs[wnd_id] = null;

        // setTimeout(() => {
        //   this.finished1 = false;
        // }, 2000);
        // // this.finished1 = false;
      }
    },
    finished2(new_f, old_f) {
      if (new_f) {
        let wnd_id = 2;
        this.raws[wnd_id] = this.get_raw(this.imgs[wnd_id]);
        this.change = !this.change;

        this.message(wnd_id);

        // this.file0.destroy();
        this.file2 = null;
        // this.imgs[wnd_id].destroy();
        this.imgs[wnd_id] = null;
        // setTimeout(() => {
        //   this.finished2 = false;
        // }, 2000);
        // // this.finished2 == false;
      }
    },
    iso(new_iso){

      // if(Object.prototype.toString.call(new_iso) != '[object Number]'){
      //   console.log(Object.prototype.toString.call(new_iso));
      //   new_iso = 32;
      // } 
      console.log(new_iso);
      if(this.vers!=undefined && this.normals!=undefined){
        this.post_raw(this.raws[0], 0, this.x_render_scale, this.y_render_scale, this.z_render_scale,new_iso);

      }
    }

    // result_fusion_states(new_state){
    //   console.log("state_change",new_state)
    // },
  },
};
</script>

<style>
.el-row {
  margin-bottom: 20px;
  /* &:last-child {
      margin-bottom: 0;
    } */
}
.el-col {
  border-radius: 4px;
}
.bg-purple-dark {
  background: #99a9bf;
}
.bg-purple {
  background: #d3dce6;
}
.bg-purple-light {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
.row-bg {
  padding: 10px 0;
  background-color: #f9fafc;
}
</style>