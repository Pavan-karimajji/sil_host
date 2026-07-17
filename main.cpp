#include <iostream>

#include "common/common.pb.h"
#include "df_interface_c.h"

// Defined in modules/perception-core/src/platform/sil/perception_core_node.cpp,
// linked directly against its already-built perception_core_sil.lib (see
// CMakeLists.txt). Not declared in a header there, so forward-declared here
// rather than pulling in perception-core's headers for one free function.
void run_sil_node();

int main() {
    // Proof that adas-interfaces' *generated* proto code (not just its hand-written
    // headers) resolves through the Conan editable pointer into modules/interfaces'
    // own build/generated/ tree - see plan.md item 12 discussion.
    adas::common::Timestamp ts;
    ts.set_seconds(42);
    std::cout << "[sil] adas::common::Timestamp from adas-interfaces: seconds="
              << ts.seconds() << "\n";

    std::cout << "[sil] ---- perception-core ----\n";
    run_sil_node();

    std::cout << "[sil] ---- df ----\n";
    std::cout << "[sil] dfApiVersion() = " << dfApiVersion() << "\n";

    void* handle = dfInit(nullptr);
    if (handle == nullptr) {
        std::cerr << "[sil] dfInit failed\n";
        return 1;
    }
    std::cout << "[sil] dfInit OK\n";

    int ok = dfExec(handle, 0.01, nullptr, nullptr, nullptr, nullptr);
    std::cout << "[sil] dfExec returned " << ok << "\n";

    dfShutdown(handle);
    std::cout << "[sil] dfShutdown OK\n";

    std::cout << "[sil] ---- done ----\n"
              << "[sil] Both components built, linked, initialized, ticked once, and "
                 "shut down cleanly in one process. No data was exchanged between them "
                 "(plan.md item 2 scope - real wiring is separate, later work).\n";
    return 0;
}
