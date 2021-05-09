<template>
  <div ref="information" class="information_detail">
    <div class="title">{{ information_title }}</div>
    <el-input size="medium " type="textarea" v-model="information_text" rows = "4"></el-input>

    <!-- <div>{{ information.window }} th window:</div>
    <div>name:{{ information.name }}</div>
    <div>type:{{ information.type }}</div>
    <div>size:{{ information.width }} * {{ information.height }}</div> -->
  </div>
</template>

<script type="text/javascript">
export default {
  name: "InformationDetail",
  props: ["information"],
  data() {
    return {
      information_text: String,
      information_title: String,
    };
  },
  components: {},

  created() {
    //   console.log("informationdetail created")
  },
  mounted() {
    this.information_text = this.StringFormat(
      "name:{0}\ntype:{1}\nsize:{2} * {3}",
      this.information.name,
      this.information.type,
      this.information.width,
      this.information.height,
    );
    this.information_title = this.StringFormat(
      "{0} th window",
      this.information.window
    );
    //   console.log(inf)
    // console.log(document.getElementById("test11"));
    // document.getElementById("test11").addEventListener("click",(e)=>{
    //   console.log(this.information0)
    // })
  },

  methods: {
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
  computed: {
    // information_text: () => {
    //   if(this.information!=undefined){
    //     return this.StringFormat("name:{0}\n type:{1}\n size:{2}",this.information.name,this.information.type,this.information.size);
    //   }
    // },
  },
  watch: {
    information(new_info) {
      this.information_text = this.StringFormat(
        "name:{0}\ntype:{1}\nsize:{2} * {3}",
        new_info.name,
        new_info.type,
        new_info.width,
        new_info.height,
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.information_detail {
  border: 1.5px solid rgb(255, 255, 255);
  border-radius: 10px;
}
.title {
  background: rgb(200, 200, 200);
}
</style>


