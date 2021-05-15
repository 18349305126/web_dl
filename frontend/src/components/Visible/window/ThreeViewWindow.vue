<template>
  <div>
    <!-- <div
      id="dicomImage"
      v-bind:style="getStyle()"
    ></div> -->

    <div ref="dicomImage"></div>
    <!-- <input id="test" type ="button" style="position: absolute;"/> -->
  </div>
</template>

<script>
//引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import * as dicomParser from "dicom-parser";
// import * as tf from "@tensorflow/tfjs";
import * as THREE from "three";

export default {
  name: "ThreeViewWindow",
  props: [
    "mat0",
    "mat1",
    "mat2",

    "width",
    "height",

    "mat0_row_spacing",
    "mat0_col_spacing",

    "mat1_row_spacing",
    "mat1_col_spacing",

    "mat2_row_spacing",
    "mat2_col_spacing",

    "label",

    "x_index",
    "y_index",
    "z_index",
  ],
  //其中mat是dicomController传过来的切片矩阵，
  //width,heigth是针对dom元素的长宽
  //mat_width，mat_height是mat的宽度高度
  //mat_row_spacing,mat_col_spacing是原dicom文件中像素距离，可以看作渲染时的缩放倍数
  //state为0时表示无任何数据，state为1时表示三维显示，state为2时表示图像融合
  data() {
    return {
      container: "",
      alpha: Number,
      view: {
        scene: "",
        renderer: "",
        camera: "",
        img_geometrys: Array,
        img_meshs: Array,
      }, //与渲染相关的变量都在这里
      control: {
        //控制相机的参数，有一些参数必须是全局变量
        speed_scale: Number,
        speed_rotate: Number,

        spher: {
          r: Number,
          theta: Number,
          pi: Number,
        },
        rect: {
          x: Number,
          y: Number,
          z: Number,
        },
      },
      init_finish: Boolean,
      wnd_states: Array,

      mat0_width: Number,
      mat0_height: Number,

      mat1_width: Number,
      mat1_height: Number,

      mat2_width: Number,
      mat2_height: Number,

      beta: Number,
      cls: Array,
      rect: "",

      mats: Array, //记录经过变形之后的mat0,mat1,mat2
      img_num: Number,
    };
  },
  created() {
    this.carmer_init(); //用于初始化相机控制参数
    this.img_num = 3;

    this.mats = new Array(this.img_num);
    this.view.img_meshs = new Array(this.img_num);
    this.view.img_geometrys = new Array(this.img_num);

    this.wnd_states = new Array([false, false, false]);
    this.cls = new Array(this.img_num);

    // this.cls[0] = { r: 1, g: 0.2, b: 0.2 };
    // this.cls[1] = { r: 0.2, g: 1, b: 0.2 };
    // this.cls[2] = { r: 0.2, g: 0.2, b: 1 };

    this.cls[0] = { r: 1, g: 1, b: 1 };
    this.cls[1] = { r: 1, g: 1, b: 1 };
    this.cls[2] = { r: 1, g: 1, b: 1 };

    this.alpha = 256;
    this.init_finish = false;
    this.beta = 1;
  },
  mounted() {
    // let element = document.getElementById("dicomImage");
    this.initRender();
    this.container.addEventListener("mousewheel", this.mousewheel, false);
    this.container.addEventListener("mousedown", this.mousedown, false);

    if (this.mats_ready()) {
      this.img_set_init();
    }
  },
  methods: {
    carmer_init() {
      this.control.speed_scale = 10;
      this.control.speed_rotate = 0.002;

      this.control.rect.x = 200;
      this.control.rect.y = 200;
      this.control.rect.z = 200; //初始相机位置

      let sp_coord = this.get_spher_coord(
        this.control.rect.x,
        this.control.rect.y,
        this.control.rect.z
      );
      this.control.spher.r = sp_coord.r;
      this.control.spher.theta = sp_coord.theta;
      this.control.spher.pi = sp_coord.pi;
    },

    get_spher_coord(x, y, z) {
      let r = Math.sqrt(x * x + y * y + z * z);
      let theta = Math.acos(z / r);
      let pi = Math.atan(y / x);
      return { r: r, theta: theta, pi: pi };
    },

    get_rect_coord(r, theta, pi) {
      let x = r * Math.sin(theta) * Math.cos(pi);
      let y = r * Math.sin(theta) * Math.sin(pi);
      let z = r * Math.cos(theta);
      return { x: x, y: y, z: z };
    },

    imgs_init() {
      for (let i = 0; i < this.img_num; i++) {
        this.view.img_geometrys[i] = new THREE.BufferGeometry();
        let material = new THREE.MeshBasicMaterial({
          vertexColors: THREE.VertexColors,
          side: THREE.DoubleSide,

          transparent: true,
          opacity: 0.95,
        }); //这里渲染方式应该是简单插值，但效果感觉不是很好
        this.view.img_meshs[i] = new THREE.Mesh(
          this.view.img_geometrys[i],
          material
        );
        this.view.scene.add(this.view.img_meshs[i]);
      }
    },

    initRender() {
      this.view.scene = new THREE.Scene();
      this.view.camera = new THREE.PerspectiveCamera(
        75,
        this.width / this.height,
        0.1,
        1500
      );
      //    this.view.camera = new THREE.OrthographicCamera( this.width / - 2, this.width / 2,this. height / 2, this.height / - 2, 0.1, 2000 );

      this.view.renderer = new THREE.WebGLRenderer();
      this.view.renderer.setSize(this.width, this.height);

      this.container = this.$refs.dicomImage;
      // const container = document.getElementById("dicomImage");
      this.container.appendChild(this.view.renderer.domElement);
      // this.container.addEventListener("mousewheel", this.mousewheel, false);
      // this.container.addEventListener("mousedown", this.mousedown, false);

      // this.view.camera.position.z = 500;
      this.view.camera.position.set(
        this.control.rect.x,
        this.control.rect.y,
        this.control.rect.z
      );
      this.view.camera.lookAt(this.view.scene.position);
      // this.view.camera.position.set(300, 300, 300);
      // this.view.camera.lookAt(new THREE.Vector3(0, 0, 0));

      this.imgs_init();

      this.render();
      this.init_finish = true;
    },

    render() {
      requestAnimationFrame(this.render);
      this.view.renderer.render(this.view.scene, this.view.camera);
    },

    mats_ready() {
      let count = 0;
      if (this.mat0 != undefined) count += 1;
      if (this.mat1 != undefined) count += 1;
      if (this.mat2 != undefined) count += 1;

      if (count >= 2) return true;
      else return false;
    },

    img_set_init() {
      if (this.mat0 != undefined && this.mat0 != null && this.mat0 != "") {
        // console.log(this.mat0);
        // console.log("recive mat0");

        this.wnd_states[0] = true;
        this.mat0_width = this.mat0.length;
        this.mat0_height = this.mat0.length;

        this.mats[0] = this.mat0;

        this.imgAdd(this.mats[0], this.alpha, this.cls[0], 0, this.z_index);
      }
      if (this.mat1 != undefined && this.mat1 != null && this.mat1 != "") {
        this.wnd_states[1] = true;
        this.mat1_width = this.mat1.length;
        this.mat1_height = this.mat1.length;

        this.mats[1] = this.mat1;

        this.imgAdd(this.mats[1], this.alpha, this.cls[1], 1, this.x_index);
      }
      if (this.mat2 != undefined && this.mat2 != null && this.mat2 != "") {
        this.wnd_states[2] = true;
        this.mat2_width = this.mat2.length;
        this.mat2_height = this.mat2.length;

        this.mats[2] = this.mat2;

        this.imgAdd(this.mats[2], this.alpha, this.cls[2], 2, this.y_index);
      }
    },

    remove_imgs() {
      let num = this.view.img_meshs.length;
      for (let i = 0; i < num; i++) {
        if (this.view.img_meshs[i] != undefined) {
          this.view.scene.remove(this.view.img_meshs[i]);
          this.view.img_meshs[i].geometry.dispose();
          this.view.img_meshs[i].material.dispose();
          this.view.img_meshs[i] = undefined;
        }
      }
    },

    mousewheel(e) {
      e.preventDefault();
      //e.stopPropagation();
      if (e.wheelDelta) {
        //判断浏览器IE，谷歌滑轮事件
        if (e.wheelDelta > 0) {
          //当滑轮向上滚动时
          if (this.view.camera.position.z > 0)
            this.view.camera.position.z -= 50;
          // fov -= near < fov ? 1 : 0;
        }
        if (e.wheelDelta < 0) {
          //当滑轮向下滚动时
          this.view.camera.position.z += 50;
          // fov += fov < far ? 1 : 0;
        }
      } else if (e.detail) {
        //Firefox滑轮事件
        if (e.detail > 0) {
          //当滑轮向上滚动时
          if (this.view.camera.position.z > 0)
            this.view.camera.position.z -= 50;
          // fov -= 1;
        }
        if (e.detail < 0) {
          //当滑轮向下滚动时
          this.view.camera.position.z += 50;
          // fov += 1;
        }
      }
      // this.view.camera.fov = fov;
      this.view.camera.updateProjectionMatrix();
      this.view.renderer.render(this.view.scene, this.view.camera);
      //updateinfo();
    },

    imgAdd(mat, alp, color_vec, wnd_id, deep) {
      // //以三角形面片为单位！！！！
      // let row = this.mat_width;
      // let col = this.mat_height;
      // console.log(row,col)
      if (mat == undefined && mat == null) return;
      let row = mat.length;
      let col = mat[0].length;
      let wid2 = row / 2;
      let hei2 = col / 2;
      if (color_vec == undefined) {
        color_vec = { r: 1, g: 1, b: 1 };
      }
      //   let z_idx = wnd_id / 10;
      // let z_idx = 0;

      let k = 0;
      let vertices = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);

      if (wnd_id == 0) {
        //表示z方向
        for (let i = 0; i < row - 1; i++) {
          for (let j = 0; j < col - 1; j++) {
            //每一个循环针对一个正方形方格，每一个正方形方格中有两个三角形面片，这个顺序很重要，不能改（我也不知道原理）
            // let p0 = [i,j,0];
            // let p1 = [i,j+1,0];
            // let p2 = [i+1,j,0];
            // let p3 = [i+1,j+1,0];

            //第一个三角形
            //第一个点
            vertices[k] = i - wid2;
            vertices[k + 1] = j - hei2;
            vertices[k + 2] = deep;
            ncolors[k] = (mat[i][j] / alp) * color_vec.r;
            ncolors[k + 1] = (mat[i][j] / alp) * color_vec.g;
            ncolors[k + 2] = (mat[i][j] / alp) * color_vec.b;

            //第二个点
            vertices[k + 3] = i + 1 - wid2;
            vertices[k + 4] = j - hei2;
            vertices[k + 5] = deep;
            ncolors[k + 3] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 4] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 5] = (mat[i + 1][j] / alp) * color_vec.b;

            //第三个点
            vertices[k + 6] = i - wid2;
            vertices[k + 7] = j + 1 - hei2;
            vertices[k + 8] = deep;
            ncolors[k + 6] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 7] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 8] = (mat[i][j + 1] / alp) * color_vec.b;

            //第二个三角形
            //第一个点
            vertices[k + 9] = i + 1 - wid2;
            vertices[k + 10] = j + 1 - hei2;
            vertices[k + 11] = deep;
            ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * color_vec.r;
            ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * color_vec.g;
            ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * color_vec.b;

            //第二个点
            vertices[k + 12] = i - wid2;
            vertices[k + 13] = j + 1 - hei2;
            vertices[k + 14] = deep;
            ncolors[k + 12] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 13] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 14] = (mat[i][j + 1] / alp) * color_vec.b;

            //第三个点
            vertices[k + 15] = i + 1 - wid2;
            vertices[k + 16] = j - hei2;
            vertices[k + 17] = deep;
            ncolors[k + 15] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 16] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 17] = (mat[i + 1][j] / alp) * color_vec.b;

            k += 18;
          }
        }

        // this.view.img_meshs[wnd_id].scale.set(0.33,0.33);
        // this.view.mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);
      } else if (wnd_id == 1) {
        //表示x方向
        for (let i = 0; i < row - 1; i++) {
          for (let j = 0; j < col - 1; j++) {
            //每一个循环针对一个正方形方格，每一个正方形方格中有两个三角形面片，这个顺序很重要，不能改（我也不知道原理）
            // let p0 = [i,j,0];
            // let p1 = [i,j+1,0];
            // let p2 = [i+1,j,0];
            // let p3 = [i+1,j+1,0];

            //第一个三角形
            //第一个点
            vertices[k] = deep;
            vertices[k + 1] = i - wid2;
            vertices[k + 2] = j - hei2;
            ncolors[k] = (mat[i][j] / alp) * color_vec.r;
            ncolors[k + 1] = (mat[i][j] / alp) * color_vec.g;
            ncolors[k + 2] = (mat[i][j] / alp) * color_vec.b;

            //第二个点
            vertices[k + 3] = deep;
            vertices[k + 4] = i + 1 - wid2;
            vertices[k + 5] = j - hei2;
            ncolors[k + 3] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 4] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 5] = (mat[i + 1][j] / alp) * color_vec.b;

            //第三个点
            vertices[k + 6] = deep;
            vertices[k + 7] = i - wid2;
            vertices[k + 8] = j + 1 - hei2;
            ncolors[k + 6] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 7] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 8] = (mat[i][j + 1] / alp) * color_vec.b;

            //第二个三角形
            //第一个点
            vertices[k + 9] = deep;
            vertices[k + 10] = i + 1 - wid2;
            vertices[k + 11] = j + 1 - hei2;
            ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * color_vec.r;
            ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * color_vec.g;
            ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * color_vec.b;

            //第二个点
            vertices[k + 12] = deep;
            vertices[k + 13] = i - wid2;
            vertices[k + 14] = j + 1 - hei2;
            ncolors[k + 12] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 13] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 14] = (mat[i][j + 1] / alp) * color_vec.b;

            //第三个点
            vertices[k + 15] = deep;
            vertices[k + 16] = i + 1 - wid2;
            vertices[k + 17] = j - hei2;
            ncolors[k + 15] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 16] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 17] = (mat[i + 1][j] / alp) * color_vec.b;

            k += 18;
          }
        }
        // console.log(vertices)
      } else if (wnd_id == 2) {
        for (let i = 0; i < row - 1; i++) {
          for (let j = 0; j < col - 1; j++) {
            //第一个三角形

            //第一个点
            vertices[k] = i + 1 - wid2;
            vertices[k + 1] = deep;
            vertices[k + 2] = j - hei2;
            ncolors[k] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 1] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 2] = (mat[i + 1][j] / alp) * color_vec.b;

            //第二个点
            vertices[k + 3] = i - wid2;
            vertices[k + 4] = deep;
            vertices[k + 5] = j - hei2;
            ncolors[k + 3] = (mat[i][j] / alp) * color_vec.r;
            ncolors[k + 4] = (mat[i][j] / alp) * color_vec.g;
            ncolors[k + 5] = (mat[i][j] / alp) * color_vec.b;

            //第三个点
            vertices[k + 6] = i - wid2;
            vertices[k + 7] = deep;
            vertices[k + 8] = j + 1 - hei2;
            ncolors[k + 6] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 7] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 8] = (mat[i][j + 1] / alp) * color_vec.b;

            //第二个三角形
            //第一个点
            vertices[k + 9] = i - wid2;
            vertices[k + 10] = deep;
            vertices[k + 11] = j + 1 - hei2;
            ncolors[k + 9] = (mat[i][j + 1] / alp) * color_vec.r;
            ncolors[k + 10] = (mat[i][j + 1] / alp) * color_vec.g;
            ncolors[k + 11] = (mat[i][j + 1] / alp) * color_vec.b;

            //第二个点
            vertices[k + 12] = i + 1 - wid2;
            vertices[k + 13] = deep;
            vertices[k + 14] = j + 1 - hei2;
            ncolors[k + 12] = (mat[i + 1][j + 1] / alp) * color_vec.r;
            ncolors[k + 13] = (mat[i + 1][j + 1] / alp) * color_vec.g;
            ncolors[k + 14] = (mat[i + 1][j + 1] / alp) * color_vec.b;

            //第三个点
            vertices[k + 15] = i + 1 - wid2;
            vertices[k + 16] = deep;
            vertices[k + 17] = j - hei2;
            ncolors[k + 15] = (mat[i + 1][j] / alp) * color_vec.r;
            ncolors[k + 16] = (mat[i + 1][j] / alp) * color_vec.g;
            ncolors[k + 17] = (mat[i + 1][j] / alp) * color_vec.b;

            k += 18;
          }
        }
        // for (let i = 0; i < row - 1; i++) {
        //   for (let j = 0; j < col - 1; j++) {

        //     //第一个三角形
        //     //第一个点
        //     vertices[k] = j - hei2;
        //     vertices[k + 1] = deep;
        //     vertices[k + 2] = i - wid2;
        //     ncolors[k] = (mat[i][j] / alp) * color_vec.r;
        //     ncolors[k + 1] = (mat[i][j] / alp) * color_vec.g;
        //     ncolors[k + 2] = (mat[i][j] / alp) * color_vec.b;

        //     //第二个点
        //     vertices[k + 3] = j - hei2;
        //     vertices[k + 4] = deep;
        //     vertices[k + 5] = i + 1- wid2;
        //     ncolors[k + 3] = (mat[i + 1][j] / alp) * color_vec.r;
        //     ncolors[k + 4] = (mat[i + 1][j] / alp) * color_vec.g;
        //     ncolors[k + 5] = (mat[i + 1][j] / alp) * color_vec.b;

        //     //第三个点
        //     vertices[k + 6] = j + 1 - hei2;
        //     vertices[k + 7] = deep;
        //     vertices[k + 8] = i - wid2;
        //     ncolors[k + 6] = (mat[i][j + 1] / alp) * color_vec.r;
        //     ncolors[k + 7] = (mat[i][j + 1] / alp) * color_vec.g;
        //     ncolors[k + 8] = (mat[i][j + 1] / alp) * color_vec.b;

        //     //第二个三角形
        //     //第一个点
        //     vertices[k + 9] = j + 1 -hei2;
        //     vertices[k + 10] = deep;
        //     vertices[k + 11] = i + 1 -wid2;
        //     ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * color_vec.r;
        //     ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * color_vec.g;
        //     ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * color_vec.b;

        //     //第二个点
        //     vertices[k + 12] = j + 1 -hei2;
        //     vertices[k + 13] = deep;
        //     vertices[k + 14] = i - wid2;
        //     ncolors[k + 12] = (mat[i][j + 1] / alp) * color_vec.r;
        //     ncolors[k + 13] = (mat[i][j + 1] / alp) * color_vec.g;
        //     ncolors[k + 14] = (mat[i][j + 1] / alp) * color_vec.b;

        //     //第三个点
        //     vertices[k + 15] = j - hei2;
        //     vertices[k + 16] = deep;
        //     vertices[k + 17] = i + 1 - wid2;
        //     ncolors[k + 15] = (mat[i + 1][j] / alp) * color_vec.r;
        //     ncolors[k + 16] = (mat[i + 1][j] / alp) * color_vec.g;
        //     ncolors[k + 17] = (mat[i + 1][j] / alp) * color_vec.b;

        //     k += 18;
        //   }
        // }
      }
      this.view.img_geometrys[wnd_id].setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );
      this.view.img_geometrys[wnd_id].setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );

      // let abnorm = 0;

      // this.view.img_geometrys[0] = new THREE.BufferGeometry();
      // this.view.img_geometrys[wnd_id].setAttribute(
      //   "position",
      //   new THREE.BufferAttribute(vertices, 3)
      // );
      // this.view.img_geometrys[wnd_id].setAttribute(
      //   "color",
      //   new THREE.BufferAttribute(ncolors, 3)
      // );
    },

    reset_beta(beta) {
      // let k = 0;
      for (let wnd_id = 0; wnd_id < this.view.img_geometrys.length; wnd_id++) {
        if (
          this.view.img_geometrys[wnd_id].getAttribute("color") != undefined
        ) {
          let ncolors = this.view.img_geometrys[wnd_id].getAttribute("color")
            .array;
          for (let i = 0; i < ncolors.length; i++) {
            ncolors[i] = ncolors[i] * beta;
          }

          this.view.img_geometrys[wnd_id].setAttribute(
            "color",
            new THREE.BufferAttribute(ncolors, 3)
          );
        }
      }
    },

    reverse_mat(mat) {
      let x = mat.length;
      let y = mat[0].length;

      let new_mat = new Array(y);
      for (let i = 0; i < y; i++) {
        new_mat[i] = new Array(x);
        for (let j = 0; j < x; j++) {
          new_mat[i][j] = mat[y - j - 1][x - i - 1];
        }
      }
      return new_mat;
    },

    getStyle() {
      let style = this.StringFormat(
        "width: {0}px;height: {1}px;top: 0px;left: 0px;position: absolute;",
        this.width,
        this.height
      );
      // console.log(style);
      return style;
    },

    mat_n(mats) {
      let sum = 0;
      for (let i = 0; i < mats.length; i++) {
        if (mats[i] != undefined) sum += 1;
      }
      return sum;
    },
    mousewheel(e) {
      e.preventDefault();
      //e.stopPropagation();
      this.scale(e);
    },
    mousedown(e) {
      const _this = this;
      if (e.button == 0) {
        // this.mouse_down_rotate(e);
        this.mouse_move_rotate(e);
      }
      this.container.onmouseup = function (e) {
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
    },

    mouse_down_rotate(e) {
      //记录当前鼠标位置，从而判断之后的旋转情况
      this.control.rotate_start.set(e.clientX, e.clientY);
    },

    mouse_move_rotate(e) {
      //当鼠标开始移动的时候
      const _this = this;

      let ori_x = e.clientX;
      let ori_y = e.clientY;

      let old_theta = this.control.spher.theta;
      let old_pi = this.control.spher.pi;

      if (e.button == 0) {
        _this.container.onmousemove = function (e) {
          //计算需要移动的距离
          let dx = e.clientX - ori_x;
          let dy = e.clientY - ori_y;

          let new_theta = old_theta - dx * _this.control.speed_rotate;
          let new_pi = old_pi - dy * _this.control.speed_rotate;

          _this.control.spher.theta = new_theta;
          _this.control.spher.pi = new_pi;

          let rect_coord = _this.get_rect_coord(
            _this.control.spher.r,
            _this.control.spher.theta,
            _this.control.spher.pi
          );

          _this.view.camera.position.set(
            rect_coord.x,
            rect_coord.y,
            rect_coord.z
          );
          _this.view.camera.lookAt(_this.view.scene.position);
        };
      }
    },

    scale(e) {
      if (e.wheelDelta) {
        //判断浏览器IE，谷歌滑轮事件
        if (e.wheelDelta > 0) {
          //当滑轮向上滚动时

          this.control.spher.r -= this.control.speed_scale;
        }
        if (e.wheelDelta < 0) {
          //当滑轮向下滚动时
          this.control.spher.r += this.control.speed_scale;
        }
      } else if (e.detail) {
        if (e.detail > 0) {
          //当滑轮向上滚动时
          this.control.spher.r -= this.control.speed_scale;
        }
        if (e.detail < 0) {
          //当滑轮向下滚动时
          this.control.spher.r += this.control.speed_scale;
        }
      }

      let rect_coord = this.get_rect_coord(
        this.control.spher.r,
        this.control.spher.theta,
        this.control.spher.pi
      );
      this.control.rect.x = rect_coord.x;
      this.control.rect.y = rect_coord.y;
      this.control.rect.z = rect_coord.z;
      this.view.camera.position.set(rect_coord.x, rect_coord.y, rect_coord.z);
    },
  },

  computed: {},

  watch: {
    // x_index(new_x) {
    //   console.log(new_x);
    // },
    // y_index(new_y) {
    //   console.log(new_y);
    // },
    // z_index(new_z) {
    //   console.log(new_z);
    // },

    mat0(new_m, old_m) {
      // console.log(this.$store.getters.visible_states)
      // if (this.$store.getters.visible_states[0] == "true") {
      //   // if (new_m != undefined && new_m != null && new_m != "") {
      //   //   // console.log("recive mat0");

      //   //   this.wnd_states[0] = true;
      //   //   this.mat0_width = new_m.length;
      //   //   this.mat0_height = new_m[0].length;

      //   //   // this.mats[0] = this.reverse_mat(new_m);
      //   //   this.mats[0] = new_m;

      //   //   this.imgAdd(this.mats[0], this.alpha, this.cls[0], 0, this.z_index);
      //   // }
      // }
      // else if(this.$store.getters.visible_states[0] == "false"){
        
      //   new_m = [[0,0],[0,0]];
      // }

      if (new_m != undefined && new_m != null && new_m != "") {
        // console.log("recive mat0");

        this.wnd_states[0] = true;
        this.mat0_width = new_m.length;
        this.mat0_height = new_m[0].length;

        // this.mats[0] = this.reverse_mat(new_m);
        this.mats[0] = new_m;

        this.imgAdd(this.mats[0], this.alpha, this.cls[0], 0, this.z_index);
      }
    },
    mat1(new_m, old_m) {
      // if (this.$store.getters.visible_states[1] == "true") {

      // }
      // else if(this.$store.getters.visible_states[1] == "false"){
      //   new_m = [[0,0],[0,0]];
      // }
      if (new_m != undefined && new_m != null && new_m != "") {
        // console.log("mat1",new_m);
        this.wnd_states[1] = true;
        this.mat1_width = new_m.length;
        this.mat1_height = new_m[0].length;

        // this.mats[1] = this.reverse_mat(new_m);
        this.mats[1] = new_m;

        this.imgAdd(this.mats[1], this.alpha, this.cls[1], 1, this.x_index);
      }
    },
    mat2(new_m, old_m) {
      // if (this.$store.getters.visible_states[2] == "true") {

      // }
      // else if(this.$store.getters.visible_states[2] == "false"){
      //   new_m = [[0,0],[0,0]];
      // }
      if (new_m != undefined && new_m != null && new_m != "") {
        // console.log("mat2",new_m);

        this.wnd_states[2] = true;
        this.mat2_width = new_m.length;
        this.mat2_height = new_m[0].length;

        // this.mats[2] = this.reverse_mat(new_m);
        this.mats[2] = new_m;
        this.imgAdd(this.mats[2], this.alpha, this.cls[2], 2, this.y_index);
      }
    },
    label(new_label, old_label) {
      // if (new_label == "z" && old_label != "z" && this.init_finish) {
      //   this.view.img_meshs[0].rotateZ(-Math.PI / 2);
      // }
    },
    "$store.state.visible.visible_states"(new_states) {
      // console.log(new_states);
    },
  },
};
</script>