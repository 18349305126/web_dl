<template>
  <div>
    <!-- <div
      id="dicomImage"
      v-bind:style="getStyle()"
    ></div> -->
    <div ref="dicomImage">
    </div>
    <!-- <input id="test" type ="button" style="position: absolute;"/> -->
  </div>
</template>

<script>
//引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import * as tf from "@tensorflow/tfjs";
import * as THREE from "three";

export default {
  name: "VisibleWindow",
  props: [
    "mat",
    "width",
    "height",
    "mat_row_spacing",
    "mat_col_spacing",
    "label",
    
    "marks",
  ],
  //其中mat是dicomController传过来的切片矩阵，
  //width,heigth是针对dom元素的长宽
  //mat_width，mat_height是mat的宽度高度
  //mat_row_spacing,mat_col_spacing是原dicom文件中像素距离，可以看作渲染时的缩放倍数
  data() {
    return {
      container: "",
      alpha:Number,//mark与img合成的alpha值
      theta: Number,//一个用于修正色彩空间的量
      beta: Number,//亮度
      view: {
        scene: "",
        renderer: "",
        camera: "",
        img_geometry: "",
        img_mesh: "",
      }, //与渲染相关的变量都在这里
      init_finish: Boolean,
      // rect: "", //(x0,y0,x1,y1)的形式
      mat_width:Number,
      mat_height:Number,


      // file: "",
      // img:"",
      // test_data:"",
    };
  },
  created() {
    // this.matting_on = false;
    // if (this.matting_state == undefined) this.matting_state = 0;
    this.alpha = 0.5;
    this.mat_width = 0;
    this.mat_height = 0;
    this.beta = 1.0;
    this.theta = 256;
    this.init_finish = false;
    this.rect = { x0: Number, y0: Number, x1: Number, y1: Number };
  },
  mounted() {
    this.initRender();
    console.log(this.marks)
    if(this.mat!=undefined &&this.mat.length > 1 && this.marks != undefined &&this.marks.length >1){
      this.img_set_init(this.mat,this.marks,this.alpha,this.theta);
    }

  },
  methods: {
    initRender() {
      this.view.scene = new THREE.Scene();
      this.view.camera = new THREE.PerspectiveCamera(
        75,
        this.width / this.height,
        0.1,
        1500
      );
      this.view.renderer = new THREE.WebGLRenderer();
      this.view.renderer.setSize(this.width, this.height);

      // this.view.img_geometrys = new THREE.BufferGeometry();
      //   let material = new THREE.MeshBasicMaterial({
      //     vertexColors: THREE.VertexColors,

      //     transparent: true,
      //     opacity: 0.5,
      //   }); //这里渲染方式应该是简单插值，但效果感觉不是很好
      //   this.view.img_meshs[i] = new THREE.Mesh(
      //     this.view.img_geometrys[i],
      //     material
      // );
      // this.view.scene.add(this.view.img_meshs[i]);

      this.container = this.$refs.dicomImage;
      // const container = document.getElementById("dicomImage");
      this.container.appendChild(this.view.renderer.domElement);
      this.container.addEventListener("mousewheel", this.mousewheel, false);
      this.container.addEventListener("mousedown", this.mousedown, false);
      // this.container.addEventListener("click", this.click, false);

      this.view.camera.position.z = 500;
      // this.view.camera.up.x = - 1;
      // this.view.camera.up.y = 0;
      this.view.camera.lookAt(new THREE.Vector3(0, 0, 0));

      this.view.img_geometry = new THREE.BufferGeometry();
      // this.view.img_geometry.center();
      let material = new THREE.MeshBasicMaterial({
        vertexColors: THREE.VertexColors,
        // transparent: true,
        // opacity: 0.5,
      }); //这里渲染方式应该是简单插值，但效果感觉不是很好
      this.view.img_mesh = new THREE.Mesh(this.view.img_geometry, material);

      if (this.label == "z") this.view.img_mesh.rotateZ(-Math.PI / 2);

      this.view.scene.add(this.view.img_mesh);

      this.render();
      this.init_finish = true;
    },
    render() {
      requestAnimationFrame(this.render);
      this.view.renderer.render(this.view.scene, this.view.camera);
    },
    reset_beta(beta) {//设置亮度
      // let k = 0;
      let ncolors = this.view.img_geometry.getAttribute("color").array;

      for (let i = 0; i < ncolors.length; i++) {
        ncolors[i] = ncolors[i] * beta;
      }
      // this.view.img_geometry = new THREE.BufferGeometry();
      this.view.img_geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      // if (this.label == "z") this.view.img_mesh.rotateZ(-Math.PI / 2);
      // this.view.img_mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);

      // this.view.img_geometry.center();
    },
   
    reverse_mat(mat) {
      let wid = mat.length;
      let hei = mat[0].length;
      let r_mat = new Array(hei);
      for (let i = 0; i < hei; i++) {
        r_mat[i] = new Array(wid);
        for (let j = 0; j < wid; j++) {
          r_mat[i][j] = mat[j][i];
        }
      }
      return r_mat;
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

    mousedown(e) {
      const _this = this;
      // console.log(this.label,"鼠标已按下");
      let disX = e.clientX;
      let disY = e.clientY;
      let o_poistion_x = this.view.camera.position.x;
      let o_poistion_y = this.view.camera.position.y;
      if (e.button == 0) {
        this.container.onmousemove = function (e) {
          //计算需要移动的距离
          let dx = e.clientX - disX;
          let dy = e.clientY - disY;
          _this.view.camera.position.x = o_poistion_x + dx;
          _this.view.camera.position.y = o_poistion_y + dy;
        };
      }

      this.container.onmouseup = function (e) {
        if (e.button == 2) {
          let dx = e.clientX - disX;
          let beta = 1 + dx / 1000;
          _this.beta = _this.beta * beta;
          if (beta <= 0.001) beta = 0.001;
          // _this.reset_beta(_this.beta);
          _this.reset_beta(
            beta
          );
        }
        _this.container.onmousemove = null;
        _this.container.onmouseup = null;
      };
      // console.log(this.container.onmousemove);
    },

    mark2rgb(mark){
      if(mark == 0)return {
        r:0,g:0,b:0
      };
      let r = Math.abs(Math.sin(mark));
      let g = Math.abs(Math.cos(mark));
      let b = Math.abs(Math.sin(2*mark));

      return { r: r, g: g, b: b };
    },

    matting(mat,marks,alpha,theta){//用于图像合成
      let row = mat.length;
      let col = mat[0].length;
      if(marks.length != mat.length || marks[0].length!= mat[0].length){
        throw new Error(
          this.StringFormat("图像与标签不匹配，影像尺寸{0},{1}，标签尺寸{2},{3}",row,col,marks.length,marks[0].length) 
        );
        return null;
      }
      let matting_mat = new Array(row);
      for (let i = 0; i < row; i++) {
        matting_mat[i] = new Array(col);
        for (let j = 0; j < col; j++) {
          matting_mat[i][j] = new Array(3);
          let rgb = this.mark2rgb(marks[i][j]);
          
          matting_mat[i][j][0] = mat[i][j]/theta * alpha +(1-alpha) * rgb.r;
          matting_mat[i][j][1] = mat[i][j]/theta * alpha +(1-alpha) * rgb.g;
          matting_mat[i][j][1] = mat[i][j]/theta * alpha +(1-alpha) * rgb.b;
        }
        
      }
      return matting_mat;
    },

    imgAdd(mat) {
      // //以三角形面片为单位！！！！
      let row = mat.length;
      let col = mat[0].length;
      let wid2 = row / 2;
      let hei2 = col / 2;

      let color_vec = { r: 1, g: 1, b: 1 };

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
          // color_vec = this.mark2color(marks[i][j]);
          vertices[k] = i - wid2;
          vertices[k + 1] = j - hei2;
          vertices[k + 2] = z_idx;
          ncolors[k] = (mat[i][j][0]); 
          ncolors[k + 1] = (mat[i][j][1]);
          ncolors[k + 2] = (mat[i][j][2]);

          //第二个点
          vertices[k + 3] = i + 1 - wid2;
          vertices[k + 4] = j - hei2;
          vertices[k + 5] = z_idx;
          ncolors[k + 3] = (mat[i + 1][j][0])
          ncolors[k + 4] = (mat[i + 1][j][1])
          ncolors[k + 5] = (mat[i + 1][j][2])

          //第三个点
          vertices[k + 6] = i - wid2;
          vertices[k + 7] = j + 1 - hei2;
          vertices[k + 8] = z_idx;
          ncolors[k + 6] = (mat[i][j + 1][0]);
          ncolors[k + 7] = (mat[i][j + 1][1]);
          ncolors[k + 8] = (mat[i][j + 1][2]);

          //第二个三角形
          //第一个点
          vertices[k + 9] = i + 1 - wid2;
          vertices[k + 10] = j + 1 - hei2;
          vertices[k + 11] = z_idx;
          ncolors[k + 9] = (mat[i + 1][j + 1][0]);
          ncolors[k + 10] = (mat[i + 1][j + 1][1]);
          ncolors[k + 11] = (mat[i + 1][j + 1][2]);

          //第二个点
          vertices[k + 12] = i - wid2;
          vertices[k + 13] = j + 1 - hei2;
          vertices[k + 14] = z_idx;
          ncolors[k + 12] = (mat[i][j + 1][0]);
          ncolors[k + 13] = (mat[i][j + 1][1]);
          ncolors[k + 14] = (mat[i][j + 1][2]);

          //第三个点
          vertices[k + 15] = i + 1 - wid2;
          vertices[k + 16] = j - hei2;
          vertices[k + 17] = z_idx;
          ncolors[k + 15] = (mat[i + 1][j][0]);
          ncolors[k + 16] = (mat[i + 1][j][1]);
          ncolors[k + 17] = (mat[i + 1][j][2]);

          k += 18;
        }
      }

      this.view.img_geometry.setAttribute(
        "position",
        new THREE.BufferAttribute(vertices, 3)
      );
      this.view.img_geometry.setAttribute(
        "color",
        new THREE.BufferAttribute(ncolors, 3)
      );
      // this.view.img_mesh.scale.set(this.mat_row_spacing, this.mat_col_spacing);

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

    img_set_init(mat,marks,alpha,theta){
      this.mat_width = mat.length;
      this.mat_height = mat[0].length;

      let matting_mat = this.matting(mat,marks,alpha,theta);

      this.imgAdd(matting_mat);
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
    StringFormat() {
      if (arguments.length == 0) return null;
      var str = arguments[0];
      for (var i = 1; i < arguments.length; i++) {
        var re = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        str = str.replace(re, arguments[i]);
      }
      return str;
    },
  },

  watch: {
    mat(new_m, old_m) {
      if (new_m != undefined && this.marks!=undefined) {
        this.img_set_init(new_m,this.marks,this.alpha,this.theta);
        
        // this.mat_width = new_m.length;
        // this.mat_height = new_m[0].length;

        // let matting_mat = this.matting(new_m,this.marks,this.alpha,this.theta);

        // this.imgAdd(matting_mat);
      }
    },
    label(new_label, old_label) {
      // if (new_label == "z" && old_label == "x" && this.init_finish) {
      //   this.view.img_mesh.rotateZ(Math.PI / 2);
      // } else if (new_label == "z" && old_label == "y" && this.init_finish) {
      //   this.view.img_mesh.rotateZ(Math.PI / 2);

      // }
      if(new_label='z' && old_label != 'z'){
        this.view.img_mesh.rotateZ(- Math.PI / 2);
      }

    },
    marks(new_marks){
      if(this.mat!=undefined && new_marks != undefined){
        // let matting_mat = this.matting(new_m,this.marks,this.alpha,this.theta);
        // this.imgAdd(matting_mat);
        this.img_set_init(this.mat,new_marks,this.alpha,this.theta);

      }
    }
    
  },
};
</script>