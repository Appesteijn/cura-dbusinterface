project(cura-dbusinterface)

cmake_minimum_required(VERSION 3.6)

install(DIRECTORY DBusInterface DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/cura/plugins)
