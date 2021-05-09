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
import * as tf from "@tensorflow/tfjs";
import * as THREE from "three";


export default {
  name: "DicomResultWindow",
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

    // "fusion_states",
    "label",
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
        fusion_geometrys: Array,
        fusion_meshs: Array,
      }, //与渲染相关的变量都在这里
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
      fusion_num: Number,
      state: Number, //状态控制，-1表示无图像，0表示图像叠加，1表示图像融合
      is_fusion: Boolean,

      
      // fusion_mat: Array,//融合功能开启后.....，不管效率了

      // file: "",
      // img:"",
      // test_data:"",
    };
  },
  created() {
    this.img_num = 3;
    this.fusion_num = 4;
    this.state = -1;

    this.is_fusion = false;

    this.mats = new Array(this.img_num);
    this.view.img_meshs = new Array(this.img_num);
    this.view.img_geometrys = new Array(this.img_num);
    this.view.fusion_geometrys = new Array(this.fusion_num);
    this.fusion_meshs = new Array(this.fusion_num);
    this.wnd_states = new Array([false, false, false]);
    this.cls = new Array(this.img_num);
    this.cls[0] ={ r: 1, g: 0.2, b: 0.2 };
    this.cls[1] ={ r: 0.2, g: 1, b: 0.2 };
    this.cls[2] ={ r: 0.2, g: 0.2, b: 1 };


    this.alpha = 256;
    this.init_finish = false;
    this.beta = 1;

    this.rect = { x0: Number, y0: Number, x1: Number, y1: Number };
  },
  mounted() {
    let element = document.getElementById("dicomImage");
    this.initRender();

    if(this.mats_ready()){
      this.img_set_init();
      
    }
  },
  methods: {
    imgs_init() {
      for (let i = 0; i < this.img_num; i++) {
        this.view.img_geometrys[i] = new THREE.BufferGeometry();
        let material = new THREE.MeshBasicMaterial({
          vertexColors: THREE.VertexColors,

          transparent: true,
          opacity: 0.5,
        }); //这里渲染方式应该是简单插值，但效果感觉不是很好
        this.view.img_meshs[i] = new THREE.Mesh(
          this.view.img_geometrys[i],
          material
        );
        this.view.scene.add(this.view.img_meshs[i]);
      }
    },
    fusion_init() {
      for (let i = 0; i < this.fusion_num; i++) {
        this.view.fusion_geometrys[i] = new THREE.BufferGeometry();
        let fusion_material = new THREE.MeshBasicMaterial({
          vertexColors: THREE.VertexColors,
        });

        this.view.fusion_meshs[i] = new THREE.Mesh(
          this.view.fusion_geometrys[i],
          fusion_material
        );
        this.view.scene.add(this.view.fusion_meshs[i]);
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
      // console.log(this.view.renderer.domElement.getBoundingClientRect());
      this.container.addEventListener("mousewheel", this.mousewheel, false);
      this.container.addEventListener("mousedown", this.mousedown, false);

      this.view.camera.position.z = 500;
      this.view.camera.lookAt(new THREE.Vector3(0, 0, 0));

      this.imgs_init();


      this.rect.x0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().x
      );
      this.rect.y0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().y
      );
      this.rect.x1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().right
      );
      this.rect.y1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().bottom
      );

      this.render();
      this.init_finish = true;
    },

    render() {
      requestAnimationFrame(this.render);
      this.view.renderer.render(this.view.scene, this.view.camera);
    },

    mats_ready(){
      let count = 0;
      if(this.mat0!=undefined)count+=1;
      if(this.mat1!=undefined)count+=1;
      if(this.mat2!=undefined)count+=1;
      
      if(count >= 2)return true;
      else return false;
    },

    img_set_init(){
      if (this.mat0 != undefined) {
        // console.log("recive mat0");

        this.wnd_states[0] = true;
        this.mat0_width = this.mat0.length;
        this.mat0_height = this.mat0.length;

        this.mats[0] = this.reverse_mat(this.mat0);
        this.state = 0;

        this.imgAdd(this.mats[0], this.alpha, this.cls[0], 0);
      }
      if (this.mat1 != undefined) {

        this.wnd_states[1] = true;
        this.mat1_width = this.mat1 .length;
        this.mat1_height = this.mat1.length;

        this.mats[1] = this.reverse_mat(this.mat1 );
        this.state = 0;

        this.imgAdd(this.mats[1], this.alpha, this.cls[1], 1);
      }
      if (this.mat2 != undefined) {
        this.wnd_states[2] = true;
        this.mat2_width = this.mat2.length;
        this.mat2_height = this.mat2.length;

        this.mats[2] = this.reverse_mat(this.mat2);
        this.state = 0;
        
        this.imgAdd(this.mats[2], this.alpha, this.cls[2], 2);
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
    remove_fusion(){
      let num = this.fusion_num;
      for (let i = 0; i < num; i++) {
        if (this.view.fusion_meshs[i] != undefined) {
          this.view.scene.remove(this.view.fusion_meshs[i]);
          this.view.fusion_meshs[i].geometry.dispose();
          this.view.fusion_meshs[i].material.dispose();
          this.view.fusion_meshs[i] = undefined;
        }
      }
    },

    get_rect(){
      let rect = {x0:'',y0:'',x1:'',y1:''};
      rect.x0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().x
      );
      rect.y0 = Number(
        this.view.renderer.domElement.getBoundingClientRect().y
      );
      rect.x1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().right
      );
      rect.y1 = Number(
        this.view.renderer.domElement.getBoundingClientRect().bottom
      );
      return rect;
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

    move(e) {
      const _this = this;
      // console.log(this.label,"鼠标已按下");
      let disX = e.clientX;
      let disY = e.clientY;
      let o_poistion_x = this.view.camera.position.x;
      let o_poistion_y = this.view.camera.position.y;
      this.container.onmousemove = function (e) {
        //计算需要移动的距离
        let dx = e.clientX - disX;
        let dy = e.clientY - disY;
        // console.log(dx,dy);
        _this.view.camera.position.x = o_poistion_x + dx;
        _this.view.camera.position.y = o_poistion_y + dy;

        //移动当前元素
        // if (t >= 0 && t <= window.innerWidth - el.offsetWidth) {
        //   el.style.left = t + "px";
        // }
      };
      // this.container.onmousemove = this.mousemove(disX,disY,o_poistion_x,o_poistion_y);
      this.container.onmouseup = function (e) {
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
    },

    change_beta(e) {
      const _this = this;
      let disX = e.clientX;

      this.container.onmouseup = function (e) {
        if (e.button == 2) {
          let dx = e.clientX - disX;
          let beta = 1 + dx / 1000;
          _this.beta = _this.beta * beta;
          if (beta <= 0.001) beta = 0.001;
          _this.reset_beta(beta);
        }
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
    },

    mousedown(e) {
      if (e.button == 0) {
        this.move(e);
      } else if (e.button == 2) {
        this.change_beta(e);
      }
    },

    click(e) {
      e.preventDefault();
      e.stopPropagation();

      if (this.fusion_states.toString() != [-1, -1, -1, -1].toString()) {
        this.fusion(e);

        // let mouse_pos = this.get_m_mouse_pos(
        //   this.rect,
        //   this.mat_width,
        //   this.mat_height,
        //   this.view.camera.position.x,
        //   this.view.camera.position.y,
        //   e.clientX,
        //   e.clientY
        // );
        // this.set_matting(
        //   mouse_pos.x,
        //   mouse_pos.y,
        //   this.mat,
        //   this.mat_width,
        //   this.mat_height,
        //   this.matting_state,
        //   this.alpha,
        //   this.beta
        // );
      }
    },

    fusion(e) {
      let PI =3.1415926;
      let fov = this.view.camera.fov/180*PI;
      let aspect = this.view.camera.aspect;
      let d = this.view.camera.position.z;
      let wid = Math.tan(fov/2) * d * 2;
      let hei = Math.tan(fov/2) * d * 2 * aspect;
      let rect = this.get_rect();
      let mouse_pos = this.get_mouse_coord(
        rect,
        wid,
        hei,
        this.view.camera.position.x,
        this.view.camera.position.y,
        e.clientX,
        e.clientY
      );
      this.remove_imgs();

      for (let i = 0; i < this.mats.length; i++) {
        if (this.mats[i] != undefined) {
          this.set_fusion(
            mouse_pos.x,
            mouse_pos.y,
            this.mats[i],
            this.alpha,
            this.beta,
            i,
            this.fusion_states,
            1
          );
        }
      }
    },

    imgAdd(mat, alp, color_vec, wnd_id) {
      // //以三角形面片为单位！！！！
      // let row = this.mat_width;
      // let col = this.mat_height;
      // console.log(row,col)
      if(mat == undefined)return;
      let row = mat.length;
      let col = mat[0].length;
      let wid2 = row / 2;
      let hei2 = col / 2;
      if (color_vec == undefined) {
        color_vec = { r: 1, g: 1, b: 1 };
      }
      //   let z_idx = wnd_id / 10;
      let z_idx = 0;

      let k = 0;
      let vertices = new Float32Array((row - 1) * (col - 1) * 6 * 3);
      let ncolors = new Float32Array((row - 1) * (col - 1) * 6 * 3);

      // let abnorm = 0;
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
          vertices[k + 2] = z_idx;
          ncolors[k] = (mat[i][j] / alp) * color_vec.r;
          ncolors[k + 1] = (mat[i][j] / alp) * color_vec.g;
          ncolors[k + 2] = (mat[i][j] / alp) * color_vec.b;

          //第二个点
          vertices[k + 3] = i + 1 - wid2;
          vertices[k + 4] = j - hei2;
          vertices[k + 5] = z_idx;
          ncolors[k + 3] = (mat[i + 1][j] / alp) * color_vec.r;
          ncolors[k + 4] = (mat[i + 1][j] / alp) * color_vec.g;
          ncolors[k + 5] = (mat[i + 1][j] / alp) * color_vec.b;

          //第三个点
          vertices[k + 6] = i - wid2;
          vertices[k + 7] = j + 1 - hei2;
          vertices[k + 8] = z_idx;
          ncolors[k + 6] = (mat[i][j + 1] / alp) * color_vec.r;
          ncolors[k + 7] = (mat[i][j + 1] / alp) * color_vec.g;
          ncolors[k + 8] = (mat[i][j + 1] / alp) * color_vec.b;

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1 - wid2;
          vertices[k + 10] = j + 1 - hei2;
          vertices[k + 11] = z_idx;
          ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * color_vec.r;
          ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * color_vec.g;
          ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * color_vec.b;

          //第二个点
          vertices[k + 12] = i - wid2;
          vertices[k + 13] = j + 1 - hei2;
          vertices[k + 14] = z_idx;
          ncolors[k + 12] = (mat[i][j + 1] / alp) * color_vec.r;
          ncolors[k + 13] = (mat[i][j + 1] / alp) * color_vec.g;
          ncolors[k + 14] = (mat[i][j + 1] / alp) * color_vec.b;

          //第三个点
          vertices[k + 15] = i + 1 - wid2;
          vertices[k + 16] = j - hei2;
          vertices[k + 17] = z_idx;
          ncolors[k + 15] = (mat[i + 1][j] / alp) * color_vec.r;
          ncolors[k + 16] = (mat[i + 1][j] / alp) * color_vec.g;
          ncolors[k + 17] = (mat[i + 1][j] / alp) * color_vec.b;

          k += 18;
        }
      }

      // this.view.img_geometrys[0] = new THREE.BufferGeometry();
      this.view.img_geometrys[wnd_id].setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );
      this.view.img_geometrys[wnd_id].setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      // if (this.label == "z") this.view.img_meshs[0].rotateZ(-Math.PI / 2);
      // this.view.img_meshs[wnd_id].scale.set(
      //   this.mat0_row_spacing,
      //   this.mat0_col_spacing
      // );

      // this.view.img_geometrys[wnd_id].center();

      //       正方形渲染的顺序，一定不能乱
      // //       var vertices = new Float32Array( [
      // // 	 0.0,  0.0,  1.0,
      // // 	 1.0,  0.0,  1.0,
      // // 	 0.0,  1.0,  1.0,

      // // 	 1.0,  1.0,  1.0,
      // // 	 0.0,  1.0,  1.0,
      // // 	 1.0,  0.0,  1.0
      // // ] );

      // this.render();
    },

    mat2vercol(mat, s_x, e_x, s_y, e_y, wid2, hei2, alp, beta) {
      let k = 0;

      let vertices = new Float32Array(
        (e_x - s_x - 1) * (e_y - s_y - 1) * 6 * 3
      );
      let ncolors = new Float32Array((e_x - s_x - 1) * (e_y - s_y - 1) * 6 * 3);
      let z_idx = 0;

      for (let i = s_x; i < e_x - 1; i++) {
        for (let j = s_y; j < e_y - 1; j++) {
          //第一个点
          vertices[k] = i - wid2;
          vertices[k + 1] = j - hei2;
          vertices[k + 2] = z_idx;

          ncolors[k] = (mat[i][j] / alp) * beta;
          ncolors[k + 1] = (mat[i][j] / alp) * beta;
          ncolors[k + 2] = (mat[i][j] / alp) * beta;

          //第二个点
          vertices[k + 3] = i + 1 - wid2;
          vertices[k + 4] = j - hei2;
          vertices[k + 5] = z_idx;
          ncolors[k + 3] = (mat[i + 1][j] / alp) * beta;
          ncolors[k + 4] = (mat[i + 1][j] / alp) * beta;
          ncolors[k + 5] = (mat[i + 1][j] / alp) * beta;

          //第三个点
          vertices[k + 6] = i - wid2;
          vertices[k + 7] = j + 1 - hei2;
          vertices[k + 8] = z_idx;
          ncolors[k + 6] = (mat[i][j + 1] / alp) * beta;
          ncolors[k + 7] = (mat[i][j + 1] / alp) * beta;
          ncolors[k + 8] = (mat[i][j + 1] / alp) * beta;

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1 - wid2;
          vertices[k + 10] = j + 1 - hei2;
          vertices[k + 11] = z_idx;
          ncolors[k + 9] = (mat[i + 1][j + 1] / alp) * beta;
          ncolors[k + 10] = (mat[i + 1][j + 1] / alp) * beta;
          ncolors[k + 11] = (mat[i + 1][j + 1] / alp) * beta;

          //第二个点
          vertices[k + 12] = i - wid2;
          vertices[k + 13] = j + 1 - hei2;
          vertices[k + 14] = z_idx;
          ncolors[k + 12] = (mat[i][j + 1] / alp) * beta;
          ncolors[k + 13] = (mat[i][j + 1] / alp) * beta;
          ncolors[k + 14] = (mat[i][j + 1] / alp) * beta;

          //第三个点
          vertices[k + 15] = i + 1 - wid2;
          vertices[k + 16] = j - hei2;
          vertices[k + 17] = z_idx;
          ncolors[k + 15] = (mat[i + 1][j] / alp) * beta;
          ncolors[k + 16] = (mat[i + 1][j] / alp) * beta;
          ncolors[k + 17] = (mat[i + 1][j] / alp) * beta;

          k += 18;
        }
      }
      return {
        vers: vertices,
        colors: ncolors,
      };
    },

    set_fusion(x, y, mat, alp, beta, wnd_id, states, num) {
      let row = mat.length;
      let col = mat[0].length;
      let wid2 = row / 2;
      let hei2 = col / 2;

      x = Math.round(x + row / 2);
      y = Math.round(y + col / 2);

      if(x > row){
        x = row - 1;
      }
      if(y > col){
        y = col - 1;
      }

      // let abnorm = 0;
      if (states[0] == wnd_id) {

        let r = this.mat2vercol(mat, 0, x, 0, y, wid2, hei2, alp, beta);
        let vertices = r.vers;
        let ncolors = r.colors;
        let state_id = 0;

        this.view.fusion_geometrys[state_id].setAttribute(
          "color",
          new THREE.BufferAttribute(ncolors, 3)
        );
        this.view.fusion_geometrys[state_id].setAttribute(
          "position",
          new THREE.BufferAttribute(vertices, 3)
        );
      }
      if (states[1] == wnd_id) {
        let r = this.mat2vercol(mat, x, row, 0, y, wid2, hei2, alp, beta);
        let vertices = r.vers;
        let ncolors = r.colors;
        let state_id = 1;

        this.view.fusion_geometrys[state_id].setAttribute(
          "color",
          new THREE.BufferAttribute(ncolors, 3)
        );
        this.view.fusion_geometrys[state_id].setAttribute(
          "position",
          new THREE.BufferAttribute(vertices, 3)
        );

      }
      if (states[2] == wnd_id) {
        let r = this.mat2vercol(mat, 0, x, y, col, wid2, hei2, alp, beta);
        let vertices = r.vers;
        let ncolors = r.colors;
        let state_id = 2;

        this.view.fusion_geometrys[state_id].setAttribute(
          "color",
          new THREE.BufferAttribute(ncolors, 3)
        );
        this.view.fusion_geometrys[state_id].setAttribute(
          "position",
          new THREE.BufferAttribute(vertices, 3)
        );

      }
      if (states[3] == wnd_id) {
        let r = this.mat2vercol(mat, x, row, y, col, wid2, hei2, alp, beta);
        let vertices = r.vers;
        let ncolors = r.colors;
        let state_id = 3;

        this.view.fusion_geometrys[state_id].setAttribute(
          "color",
          new THREE.BufferAttribute(ncolors, 3)
        );
        this.view.fusion_geometrys[state_id].setAttribute(
          "position",
          new THREE.BufferAttribute(vertices, 3)
        );

      }

      // this.view.img_geometrys[wnd_id].setAttribute(
      //   "color",
      //   new THREE.BufferAttribute(ncolors, 3)
      // );
      // this.view.img_geometrys[wnd_id].setAttribute(
      //   "position",
      //   new THREE.BufferAttribute(vertices, 3)
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

    get_mouse_coord(
      rect,
      m_wid,
      m_hei,
      m_center_x,
      m_center_y,
      mouse_x,
      mouse_y
    ) {
      let cx = (rect.x0 + rect.x1) / 2;
      let cy = (rect.y0 + rect.y1) / 2;
      let wid = rect.x1 - rect.x0;
      let hei = rect.y1 - rect.y0;
      // let disX = e.clientX;
      // let disY = e.clientY;
      let dx = mouse_x - cx;
      let dy = mouse_y - cy;

      dx = (m_wid / wid) * dx;
      dy = - (m_hei / hei) * dy;
      let m_mouse_pos = {
        x: m_center_x + dx,
        y: m_center_y + dy,
      };
      // console.log(m_mouse_pos.x,m_mouse_pos.y)

      // console.log(rect);
      // console.log(m_mouse_pos);
      // console.log(mouse_pos);
      return m_mouse_pos;
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
  },

  computed:{
    fusion_states(){
      return this.$store.getters.fusion_states;
      // return this.$store.state.visible.fusion_states;
    }
  },

  watch: {
    mat0(new_m, old_m) {
      if (new_m != undefined) {
        // console.log("recive mat0");

        this.wnd_states[0] = true;
        this.mat0_width = new_m.length;
        this.mat0_height = new_m[0].length;
        // this.imgAdd(
        //   new_m,
        //   this.alpha,
        //   cl,
        //   0
        // );
        this.mats[0] = this.reverse_mat(new_m);
        this.state = 0;

        this.imgAdd(this.mats[0], this.alpha, this.cls[0], 0);
      }
    },
    mat1(new_m, old_m) {
      if (new_m != undefined) {
        // console.log("recive mat1");
        this.wnd_states[1] = true;
        this.mat1_width = new_m.length;
        this.mat1_height = new_m[0].length;
        // this.imgAdd(
        //   new_m,
        //   this.alpha,
        //   cl,
        //   1
        // );

        this.mats[1] = this.reverse_mat(new_m);
        this.state = 0;

        this.imgAdd(this.mats[1], this.alpha, this.cls[1], 1);
      }
    },
    mat2(new_m, old_m) {
      if (new_m != undefined) {
        // console.log("recive mat1");
        this.wnd_states[2] = true;
        this.mat2_width = new_m.length;
        this.mat2_height = new_m[0].length;
        // this.imgAdd(
        //   new_m,
        //   this.alpha,
        //   cl,
        //   2
        // );
        this.mats[2] = this.reverse_mat(new_m);
        this.state = 0;

        this.imgAdd(this.mats[2], this.alpha, this.cls[2], 2);
      }
    },
    label(new_label, old_label) {
      // if (new_label == "z" && old_label != "z" && this.init_finish) {
      //   this.view.img_meshs[0].rotateZ(-Math.PI / 2);
      // }
    },
    fusion_states(new_fusion_states) {

      if (new_fusion_states.toString() != [-1, -1, -1, -1].toString() && this.state == 0) {
        this.is_fusion = true;
        this.state = 1;
      }
      if (new_fusion_states.toString() != [-1, -1, -1, -1].toString() &&this.state == 1) {
        this.fusion_init();
        this.container.addEventListener("click", this.click, false);
      }
      
      else if(new_fusion_states.toString() == [-1, -1, -1, -1].toString() &&this.state == 1){
        this.remove_fusion();
        this.imgs_init();
        for (let i = 0; i < this.img_num; i++) {
          if(this.mats[i] != undefined){
            this.imgAdd(this.mats[i], this.alpha, this.cls[i], i);

          }          
        }
      }
    },
  },
};
</script>