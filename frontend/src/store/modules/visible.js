const state = {
    result_view_state : 0,//0表示默认体渲染，1表示fusion，2表示标签标记
    fusion_states : [-1,-1,-1,-1],
}

const mutations = {
    RESET_RESULT_VIEW_STATE :(state,result_view_state) => {
        state.result_view_state = result_view_state;
    },
    RESET_FUSION_STATES:(state,fusion_states) =>{
        state.fusion_states = fusion_states;
    },
}

const actions = {
    
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
}