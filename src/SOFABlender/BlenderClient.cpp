#include <sofa/core/ObjectFactory.h>
#include <SOFABlender/BlenderClient.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/core/visual/VisualModel.h>

namespace sofablender
{
int BlenderClientClass = sofa::core::RegisterObject("Client sending data to a Blender server")
    .add< BlenderClient >();

BlenderClient::BlenderClient()
    : m_socket(m_ioService)
{
    f_listening.setValue(true);
}

void BlenderClient::init()
{
    BaseObject::init();

    try
    {
        m_serverEndpoint = std::make_unique<boost::asio::ip::tcp::endpoint>(
            boost::asio::ip::address::from_string("127.0.0.1"), 12345);

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
