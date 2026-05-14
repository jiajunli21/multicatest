package com.multica.points.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.multica.points.entity.PointsFreeze;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.math.BigDecimal;

@Mapper
public interface PointsFreezeMapper extends BaseMapper<PointsFreeze> {

    @Select("SELECT COALESCE(SUM(amount), 0) FROM points_freeze WHERE user_id = #{userId} AND status = 'FROZEN'")
    BigDecimal sumFrozenAmount(@Param("userId") String userId);

    @Update("UPDATE points_freeze SET status = #{status} WHERE id = #{id} AND status = #{currentStatus}")
    int updateStatus(@Param("id") Long id, @Param("status") String status, @Param("currentStatus") String currentStatus);
}
