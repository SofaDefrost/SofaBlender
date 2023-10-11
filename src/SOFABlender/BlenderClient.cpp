#include <sofa/core/ObjectFactory.h>
#include <SOFABlender/BlenderClient.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/core/visual/VisualModel.h>

namespace sofablender
{
int BlenderClientClass = sofa::core::RegisterObject("Client sending data to a Blender server")
    .add< BlenderClient >();

BlenderClient::BlenderClient()
    : d_host(initData(&d_host, std::string("127.0.0.1"), "host",
                      "Network address of the device running the server"))
    , d_port(initData(&d_port, 12345u, "port",
                      "Numeric value (ranging from 0 to 65535) identifying a communication channel with the server"))
    , m_socket(m_ioService)
{
    f_listening.setValue(true);
}

void BlenderClient::init()
{
    BaseObject::init();

    try
    {
        m_serverEndpoint = std::make_unique<boost::asio::ip::tcp::endpoint>(
            boost::asio::ip::address::from_string(d_host.getValue()), d_port.getValue());

        m_socket.connect(*m_serverEndpoint);
    }
    catch (std::exception& e)
    {
        msg_error() << "Initialization failed: " << e.what();
        this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
        return;
    }

    sendData();
    ++m_nbIterations;

    this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Valid);
}

void BlenderClient::cleanup()
{
    BaseObject::cleanup();
    if (this->isComponentStateValid())
    {
        m_socket.close();
    }
}

void BlenderClient::handleEvent(sofa::core::objectmodel::Event* event)
{
    if (sofa::simulation::AnimateBeginEvent::checkEventType(event))
    {
        onBeginAnimationStep();
    }
}

void BlenderClient::sendData()
{
    if (!this->isComponentStateValid())
    {
        return;
    }

    std::stringstream message;

    message << m_nbIterations << " ";

    const auto visualModels = this->getContext()->getObjects<sofa::core::visual::VisualModel>(sofa::core::objectmodel::BaseContext::SearchDown);
    message << visualModels.size();



    boost::asio::write(m_socket, boost::asio::buffer(message.str()));
}

void BlenderClient::onBeginAnimationStep()
{
    sendData();
    ++m_nbIterations;
}


}
