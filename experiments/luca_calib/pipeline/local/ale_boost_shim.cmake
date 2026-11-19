# Injected after project(ale) via CMAKE_PROJECT_ale_INCLUDE (ALE's own files are not edited).
# conda-forge's BoostConfig (b2-built) has no targets for header-only components, but ALE's
# src/CMakeLists.txt links Boost::algorithm and Boost::math. Provide them as header-only targets.
foreach(_c algorithm math)
  if(NOT TARGET Boost::${_c})
    add_library(Boost::${_c} INTERFACE IMPORTED GLOBAL)
    set_target_properties(Boost::${_c} PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${ALE_ENV_PREFIX}/include")
  endif()
endforeach()
