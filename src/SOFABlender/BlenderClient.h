#pragma once
#include <SOFABlender/config.h>
#include <sofa/core/objectmodel/BaseObject.h>

#define BOOST_DATE_TIME_NO_LIB
#include <boost/asio.hpp>

namespace sofablender
{

class SOFA_SOFABLENDER_API BlenderClient : public sofa::core::objectmodel::BaseObject
{
public:
    SOFA_CLASS(BlenderClient, sofa::core::objectmodel::BaseObject);

    BlenderClient();
    void init() override;
    void cleanup() override;
    void handleEvent( sofa::core::objectmodel::Event* event ) override;

private:
    boost::asio::io_service m_ioService;
    boost::asio::ip::tcp::socket m_socket;

    std::unique_ptr<boost::asio::ip::tcp::endpoint> m_serverEndpoint;


    void sendData();
    std::size_t m_nbIterations {};

    void onBeginAnimationStep();
};

}
